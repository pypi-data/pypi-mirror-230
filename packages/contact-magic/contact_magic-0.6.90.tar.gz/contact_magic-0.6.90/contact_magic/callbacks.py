"""
Callbacks only accept the row that was finished and the current campaign.

Callbacks must return the DataRow.

"""
from contact_magic import DataRow, PersonalizationSettings
from contact_magic.dict_utils import get_first_level_items
from contact_magic.integrations.copyfactory import create_contact_in_copyfactory


async def add_as_contact_to_copyfactory(
    data_row: DataRow, campaign: PersonalizationSettings
) -> DataRow:
    """
    Agency callback to automatically add new
    processed contacts to Copyfactory to trigger
    a sync with a CRM or sales automation platform.
    """
    email_col_value = data_row.get_values_by_key_name(
        "Email"
    ) or data_row.get_values_by_key_name("email")
    if not email_col_value:
        return data_row
    # These are generated columns we don't want to push to CF.
    custom_cols_exclude = campaign.get_datapoint_column_names + [
        "domain_to_check",
        "location_search_from",
        "search_query",
        "email",
        "is_approved",
        "Email",
    ]
    await create_contact_in_copyfactory(
        sequence_id=campaign.campaign_meta_data.get("sequence_id"),
        mapping_id=campaign.campaign_meta_data.get("mapping_id"),
        email=email_col_value[0],
        sentence_fields={
            k.replace("__", "_"): data_row.data.get(k)
            for k in campaign.get_datapoint_column_names
            if not k.startswith("source__")
        },
        custom_fields={
            f"cus_{k}": v
            for k, v in get_first_level_items(data_row.data).items()
            if k not in custom_cols_exclude and not k.startswith("technology__")
        },
    )
    return data_row
