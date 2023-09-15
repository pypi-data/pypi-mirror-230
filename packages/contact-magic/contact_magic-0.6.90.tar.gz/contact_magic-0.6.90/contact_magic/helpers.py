from urllib.parse import urlparse

import gspread
import numpy as np
import pandas as pd

from contact_magic.callbacks import add_as_contact_to_copyfactory
from contact_magic.conf.settings import SETTINGS
from contact_magic.integrations.copyfactory import get_sequence_id_by_name
from contact_magic.integrations.sheets import (
    get_all_values_from_sheet,
    get_all_worksheets_in_spreadsheet,
    get_worksheet_from_spreadsheet,
)
from contact_magic.models import PersonalizationSettings


def prepare_data_for_gsheet(
    df: pd.DataFrame, mapping: dict = None, enforced_columns: list = None
):
    """
    Converts a dataframe to a list of list to be passed to Gspread or Sheet alternative.
    Can pass a mapping where the key names are columns in the Dataframe.
        The values represent an object of data to be switched.
        Ex: mapping={"is_approved": {'TRUE': True, 'FALSE': False}
    Handy for when converting 'TRUE' as a sting into True as a boolean for
    consistent types in the Google sheet.

    Enforced columns is a list of columns where if rows don't have all the
    columns in the list the row is dropped.
    """
    if isinstance(mapping, dict):
        for col_name, map_conversion in mapping.items():
            if col_name in df:
                df.loc[:, col_name] = df[col_name].map(map_conversion)
    if enforced_columns := enforced_columns or []:
        df = df[df[enforced_columns].notna().all(axis=1)]
    df = df.fillna("")
    return [df.columns.values.tolist()] + df.values.tolist()


def parse_mapping_url(url: str) -> dict:
    split_parsed_url_path = urlparse(url).path.strip("/").split("/")
    return {
        "mapping_id": split_parsed_url_path[-1],
        "profile_id": split_parsed_url_path[1],
    }


def get_personalization_settings_from_sheet(
    main_workflow_sheet: gspread.Spreadsheet,
    worksheet_name="settings",
    sequence_name: str = None,
    mapping_url: str = None,
) -> PersonalizationSettings:
    """
    Converts a google sheet into a PersonalizationSettings instance.
    """
    settings = []
    settings_sheet = get_worksheet_from_spreadsheet(main_workflow_sheet, worksheet_name)
    settings_data = get_all_values_from_sheet(settings_sheet)
    df_settings_data = pd.DataFrame(
        data=settings_data[1:], columns=settings_data[0]
    ).replace("", np.nan)

    for i in range(0, len(df_settings_data.columns), 2):
        scraper_col_values = list(df_settings_data.iloc[:, i].values)
        if not scraper_col_values:
            continue
        new_entry = {"col_name": df_settings_data.columns[i], "sentence_wizards": []}
        scrapers_seen = set()
        for position, scraper in enumerate(scraper_col_values):
            if SETTINGS.ALLOWED_SCRAPER_NAMES and (
                scraper not in SETTINGS.ALLOWED_SCRAPER_NAMES
                or scraper in scrapers_seen
            ):
                continue
            premise_url = df_settings_data.iloc[position, i + 1]
            if pd.isnull(premise_url):
                continue
            if scraper == "FALLBACK":
                new_entry["sentence_wizards"].append(
                    {"scraper_name": scraper, "fallback_template": premise_url}
                )
            elif scraper == "USE_HISTORIC_DATA":
                new_entry["sentence_wizards"].append(
                    {
                        "scraper_name": None,
                        "premise_url": premise_url,
                        "restrict_to_scraped_data": False,
                    }
                )
            else:
                new_entry["sentence_wizards"].append(
                    {"scraper_name": scraper, "premise_url": premise_url}
                )
            scrapers_seen.add(scraper)
        if new_entry.get("sentence_wizards"):
            settings.append(new_entry)

    try:
        categories = []
        # Try to get tech category settings
        sheet_names = [
            sheet.title
            for sheet in get_all_worksheets_in_spreadsheet(main_workflow_sheet)
        ]
        tech_settings_sheet_name = "technology_settings"
        if tech_settings_sheet_name in sheet_names:
            tech_settings_sheet = get_worksheet_from_spreadsheet(
                main_workflow_sheet, tech_settings_sheet_name
            )
            tech_category_settings_data = get_all_values_from_sheet(tech_settings_sheet)
            df_settings_data = pd.DataFrame(
                data=tech_category_settings_data[1:],
                columns=tech_category_settings_data[0],
            ).replace("", np.nan)
            df_settings_data = df_settings_data.loc[
                df_settings_data["category"].notna()
            ]
            allowed_cats = df_settings_data.loc[df_settings_data["include"] == "TRUE"]
            if not allowed_cats.empty:
                categories = list(allowed_cats["category"].values)
        else:
            categories = []
    except Exception:
        categories = []
    meta_data = {}
    callbacks = []
    sequence_name = "Untitled sequence" if pd.isna(sequence_name) else sequence_name
    if mapping_url:
        parsed_url_items = parse_mapping_url(mapping_url)
        sequence_id = get_sequence_id_by_name(
            profile_id=parsed_url_items.get("profile_id"), sequence_name=sequence_name
        )
        meta_data = parsed_url_items | {"sequence_id": sequence_id}
        callbacks.append(add_as_contact_to_copyfactory)
    return PersonalizationSettings(
        datapoints=settings,
        allowed_technology_categories=categories,
        name=sequence_name,
        campaign_meta_data=meta_data,
        row_callback=callbacks,
    )


def worksheet_to_dataframe(
    main_workflow_sheet: gspread.Spreadsheet, tab_name="WorkingSheet"
) -> pd.DataFrame:
    """
    Convert a tab into a Dataframe.
    """
    worksheet = get_worksheet_from_spreadsheet(main_workflow_sheet, tab_name)
    tab_working_data = get_all_values_from_sheet(worksheet)
    return pd.DataFrame(data=tab_working_data[1:], columns=tab_working_data[0]).replace(
        "", np.nan
    )
