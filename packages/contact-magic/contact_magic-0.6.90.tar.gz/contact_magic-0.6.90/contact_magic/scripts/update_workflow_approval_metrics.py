import numpy as np
import pandas as pd

from contact_magic.conf.settings import SETTINGS
from contact_magic.helpers import worksheet_to_dataframe
from contact_magic.integrations.sheets import (
    get_cell_from_sheet,
    get_spreadsheet_by_url,
    get_worksheet_from_spreadsheet,
    update_cell,
)
from contact_magic.scripts.logger import logger
from contact_magic.utils import is_google_workflow_url_valid


def update_rows_approved_and_remaining():
    workflows_sheet = get_worksheet_from_spreadsheet(
        get_spreadsheet_by_url(SETTINGS.MASTERSHEET_URL), "Workflows"
    )
    workflow_values = workflows_sheet.get_all_values()
    df = pd.DataFrame(data=workflow_values[1:], columns=workflow_values[0]).replace(
        "", np.nan
    )
    for i, row in df.iterrows():
        if not all(field in row for field in ["WorkflowUrl", "ClientName"]):
            continue
        if is_google_workflow_url_valid(row["WorkflowUrl"]):
            try:
                data = worksheet_to_dataframe(
                    get_spreadsheet_by_url(row["WorkflowUrl"]), "WorkingSheet"
                )
            except Exception:
                continue
            if not all(field in data.columns for field in ["Website", "is_approved"]):
                continue
            logger.info(
                "updating_rows_appproved",
                row_number=i + 2,
                sequence_name=row["WorkflowName"],
                client_name=row["ClientName"],
                status="STARTING",
            )
            total_rows = len(data.dropna(subset=["Website"]))
            total_approved_data = len(data.loc[data["is_approved"] == "TRUE"])
            if total_rows > 0:
                approved_percentage = round(total_approved_data / total_rows, 2)
            else:
                approved_percentage = 0
            base = 5
            for num, metric in enumerate(
                [total_rows, total_approved_data, approved_percentage], 1
            ):
                cell = get_cell_from_sheet(
                    workflows_sheet, row=i + 2, column=base + num
                )
                cell.value = metric
                update_cell(workflows_sheet, cell.row, cell.col, cell.value)
            logger.info(
                "updating_rows_appproved",
                row_number=i + 2,
                sequence_name=row["WorkflowName"],
                client_name=row["ClientName"],
                status="COMPLETE",
            )


if __name__ == "__main__":
    update_rows_approved_and_remaining()
