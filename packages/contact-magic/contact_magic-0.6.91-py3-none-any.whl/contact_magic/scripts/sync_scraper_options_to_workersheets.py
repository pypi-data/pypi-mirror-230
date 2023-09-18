import asyncio

import numpy as np
import pandas as pd

from contact_magic.conf.all_technology_categories import ALL_CATEGORIES
from contact_magic.conf.settings import SETTINGS
from contact_magic.integrations import make_sales_scraper_request
from contact_magic.integrations.sheets import (
    bulk_update,
    clear_sheet,
    create_new_worksheet,
    get_all_values_from_sheet,
    get_all_worksheets_in_spreadsheet,
    get_spreadsheet_by_url,
    get_worksheet_from_spreadsheet,
)
from contact_magic.scripts.default_scraper_options import default_scraper_options
from contact_magic.scripts.logger import logger
from contact_magic.utils import is_google_workflow_url_valid


async def get_user_scrapers_as_df():
    res = await make_sales_scraper_request(endpoint="custom-scrapers", data={})
    user_scrapers_as_df = pd.json_normalize(data=res)
    user_scrapers_as_df = user_scrapers_as_df.rename(
        columns={
            "scraper_slug_name": "Scraper",
            "scraper_properties.description": "Scraper Description",
        }
    )
    user_scrapers_as_df["Scraper"] = (
        user_scrapers_as_df["api_namespace"] + "/" + user_scrapers_as_df["Scraper"]
    )
    user_scrapers_as_df["Notes"] = ""
    return user_scrapers_as_df[["Scraper", "Scraper Description", "Notes"]]


def sync_scraper_options(scraper_options_df=default_scraper_options):
    workflows_sheet = get_worksheet_from_spreadsheet(
        get_spreadsheet_by_url(SETTINGS.MASTERSHEET_URL), "Workflows"
    )
    workflow_values = get_all_values_from_sheet(workflows_sheet)
    df = pd.DataFrame(data=workflow_values[1:], columns=workflow_values[0]).replace(
        "", np.nan
    )
    user_scrapers = asyncio.run(get_user_scrapers_as_df())
    final_df = pd.concat([scraper_options_df, user_scrapers])
    for i, row in df.iterrows():
        if is_google_workflow_url_valid(row["WorkflowUrl"]):
            logger.info(
                "updating_scraper_options",
                row_number=i + 2,
                sequence_name=row["WorkflowName"],
                client_name=row["ClientName"],
                status="STARTING",
            )
            try:
                ss = get_spreadsheet_by_url(row["WorkflowUrl"])
                ws = get_worksheet_from_spreadsheet(ss, "scraper_options")
            except Exception:
                continue
            clear_sheet(ws)
            bulk_update(
                ws,
                [final_df.columns.values.tolist()] + final_df.values.tolist(),
            )
            # Create tech options
            sheet_names = [
                sheet.title for sheet in get_all_worksheets_in_spreadsheet(ss)
            ]
            tech_settings_sheet_name = "technology_settings"
            if tech_settings_sheet_name not in sheet_names:
                build_technology_sheet(ss, tech_settings_sheet_name)
            logger.info(
                "updating_scraper_options",
                row_number=i + 2,
                sequence_name=row["WorkflowName"],
                client_name=row["ClientName"],
                status="COMPLETE",
            )


def build_technology_sheet(spreadsheet, tech_settings_sheet_name):
    worksheet = create_new_worksheet(
        spreadsheet, tech_settings_sheet_name, len(ALL_CATEGORIES) + 10, 2
    )
    bulk_update(
        worksheet, [["category", "include"]] + [[cat, False] for cat in ALL_CATEGORIES]
    )
