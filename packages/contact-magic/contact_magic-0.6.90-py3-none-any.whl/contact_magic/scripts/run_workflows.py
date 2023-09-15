import datetime

try:
    import gspread
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "You do not have the Sheets extension installed."
        " Run `pip install contact-magic[sheets]`"
    )
import numpy as np
import pandas as pd
import pytz

from contact_magic.conf import settings as global_settings
from contact_magic.conf.settings import SETTINGS
from contact_magic.helpers import (
    get_personalization_settings_from_sheet,
    prepare_data_for_gsheet,
    worksheet_to_dataframe,
)
from contact_magic.integrations.sheets import (
    bulk_update,
    format_range,
    get_all_values_from_sheet,
    get_spreadsheet_by_url,
    get_worksheet_from_spreadsheet,
    update_cell,
)
from contact_magic.scripts.logger import logger
from contact_magic.utils import chunk_df, convert_to_a1, is_google_workflow_url_valid


def get_workflows_to_run(sheet):
    """
    Filter for only active workflows & ones with workflows URLs.
    """
    workflow_values = get_all_values_from_sheet(sheet)
    df = pd.DataFrame(data=workflow_values[1:], columns=workflow_values[0]).replace(
        "", np.nan
    )
    workflows_to_run = df.loc[df["RunWorkflow"] == "TRUE"]
    return workflows_to_run[workflows_to_run["WorkflowUrl"].notna()]


def update_date_last_ran(
    worksheet: gspread.Worksheet, row_number: int, col_number: int = 5
):
    """
    Update a cell with the latest date based on the configured timezone.
    """
    timezone = pytz.timezone(SETTINGS.TIMEZONE)
    current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
    cell = worksheet.cell(row=row_number, col=col_number)
    cell.value = current_time
    update_cell(worksheet, cell.row, cell.col, cell.value)


def filter_out_row(row) -> bool:
    if row["is_approved"] == "TRUE":
        return True
    return bool(pd.isnull(row["Website"]))


def uncheck_rows_and_format(sheet, df: pd.DataFrame, col_number=4):
    for i, row in df.iterrows():
        row_num = i + 2
        update_cell(sheet, row_num, col_number, False)
        format_range(
            sheet,
            f"{row_num}:{row_num}",
            {
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.3},
            },
        )


def mark_row_as_completed(sheet, row_number):
    row_num = row_number + 2
    format_range(
        sheet,
        f"{row_num}:{row_num}",
        {
            "backgroundColor": {"red": 0.0, "green": 1.0, "blue": 0.0},
        },
    )


def run_sheets(return_as_arguments=False):
    workflows_sheet = get_worksheet_from_spreadsheet(
        get_spreadsheet_by_url(SETTINGS.MASTERSHEET_URL), "Workflows"
    )
    workflows_to_run = get_workflows_to_run(workflows_sheet)
    uncheck_rows_and_format(workflows_sheet, workflows_to_run)

    tasks = []
    for i, row in workflows_to_run.iterrows():
        if not is_google_workflow_url_valid(row["WorkflowUrl"]):
            continue
        workflow_sheet = get_spreadsheet_by_url(row["WorkflowUrl"])
        filtered_working_data = worksheet_to_dataframe(workflow_sheet)
        # Don't filter working data since need to maintain
        # index so do spoof check to know if any rows to process.
        if (
            filtered_working_data.loc[filtered_working_data["is_approved"] == "FALSE"]
            .dropna(subset=["Website"])
            .empty
        ):
            continue
        if return_as_arguments:
            tasks.append(
                (
                    process_worksheet,
                    {
                        "filtered_working_data": filtered_working_data,
                        "i": i,
                        "row": row,
                        "workflow_sheet": workflow_sheet,
                        "workflows_sheet": workflows_sheet,
                    },
                )
            )
        else:
            process_worksheet(
                filtered_working_data, i, row, workflow_sheet, workflows_sheet
            )
    return tasks


def process_worksheet(filtered_working_data, i, row, workflow_sheet, workflows_sheet):
    logger.info(
        "running_workflow",
        row_number=i + 2,
        dataset_size=len(filtered_working_data),
        sequence_name=row["WorkflowName"],
        client_name=row["ClientName"],
        status="STARTING",
    )

    # Create boolean masks for NaN values and set cols with NA vals.
    for col in ["domain_to_check", "location_search_from", "search_query"]:
        if col not in filtered_working_data.columns:
            filtered_working_data[col] = np.NaN

    # Set masks to cols we need to generate
    domain_check_mask = filtered_working_data["domain_to_check"].isna()
    location_search_mask = filtered_working_data["location_search_from"].isna()
    search_query_mask = filtered_working_data["search_query"].isna()

    # Assign domain to check where domain_to_check is NaN
    filtered_working_data.loc[
        domain_check_mask, "domain_to_check"
    ] = filtered_working_data.loc[domain_check_mask, "Website"]

    # Assign default location to search if not already set
    location_search_from = (
        filtered_working_data[["City", "State", "Country"]]
        .fillna("")
        .agg(" ".join, axis=1)
        .str.strip()
    )
    filtered_working_data.loc[
        location_search_mask, "location_search_from"
    ] = location_search_from[location_search_mask]

    # Assign default search query if not already set based on ["Company Name", "City"]
    search_query = (
        filtered_working_data[["Company Name", "City", "State", "Country"]]
        .fillna("")
        .agg(" ".join, axis=1)
        .str.strip()
    )
    filtered_working_data.loc[search_query_mask, "search_query"] = search_query[
        search_query_mask
    ]
    mapping_url = None
    if "MappingUrl" in row:
        mapping_url = None if pd.isna(row["MappingUrl"]) else row["MappingUrl"]

    campaign_settings = get_personalization_settings_from_sheet(
        workflow_sheet, sequence_name=row["WorkflowName"], mapping_url=mapping_url
    )
    offset = 0
    working_sheet = get_worksheet_from_spreadsheet(workflow_sheet, "WorkingSheet")

    # Track the existing columns - use list since order matters.
    df_cols = list(filtered_working_data.columns)
    current_header = []

    for chunk in chunk_df(
        filtered_working_data,
        global_settings.DATA_CHUNK_SIZE or len(filtered_working_data),
    ):
        # Before processing add any columns we don't already have.
        chunk = chunk.assign(
            **{col: np.nan for col in df_cols if col not in chunk.columns}
        )
        processed_data = campaign_settings.process_from_dataframe(
            df=chunk, exclude_filter_func=filter_out_row
        )
        # Add new columns
        [df_cols.append(col) for col in processed_data.columns if col not in df_cols]
        data = prepare_data_for_gsheet(
            processed_data,
            {"is_approved": {"TRUE": True, "FALSE": False}},
            enforced_columns=["Website"],
        )
        # Update header row for any added cols.
        if len(df_cols) > len(current_header):
            bulk_update(
                working_sheet,
                f"A1:{convert_to_a1(row=1, col=len(df_cols))}",
                [df_cols],
            )
            current_header = df_cols
        row_data = data[1:]
        start = convert_to_a1(row=2 + offset, col=1)
        offset += global_settings.DATA_CHUNK_SIZE
        if not row_data:
            continue
        row_num = len(row_data) + 1 + offset
        if row_num > len(filtered_working_data):
            row_num = len(filtered_working_data) + 1
        end = convert_to_a1(row=row_num, col=len(processed_data.columns))
        bulk_update(working_sheet, f"{start}:{end}", row_data)

    update_date_last_ran(workflows_sheet, i + 2)
    logger.info(
        "running_workflow",
        row_number=i + 2,
        dataset_size=len(filtered_working_data),
        sequence_name=row["WorkflowName"],
        client_name=row["ClientName"],
        status="COMPLETE",
    )
    row = row.fillna("")
    SETTINGS.notify_webhook(
        "worksheet_complete",
        {
            "client_name": row["ClientName"],
            "sequence_name": row["WorkflowName"],
            "workflow_url": row["WorkflowUrl"],
        },
    )
    mark_row_as_completed(workflows_sheet, i)


if __name__ == "__main__":
    run_sheets()
