import asyncio
import re
from datetime import datetime
from typing import Any, Callable, Coroutine, List, Union
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from pydantic import AnyUrl, BaseModel, Field, validator

from contact_magic.asyncio import do_bulk
from contact_magic.conf.all_technology_categories import (
    ALL_CATEGORIES,
    DEFAULT_TRACKABLE_CATEGORIES,
)
from contact_magic.conf.settings import SETTINGS
from contact_magic.dict_utils import (
    delete_key_in_object,
    get_values_in_object_by_key,
    replace_keys_in_object,
    replace_values_in_object,
)
from contact_magic.integrations import (
    make_copyfactory_request,
    make_sales_scraper_request,
)
from contact_magic.logger import logger
from contact_magic.utils import get_id_from_url, is_valid_premise_url

SALES_SCRAPER_KEY_PREFIX_NAME = "sales_scrapers"


class DataRow(BaseModel):
    """
    A class to hold a row of data and it's index number
    to sort by after. Converts set data to a dict.
    """

    data: Any
    index: int
    _original_type = None

    @validator("data")
    def validate_data(cls, value):
        if not isinstance(value, pd.Series) and not isinstance(value, dict):
            raise ValueError("Data must be either type pd.Series or Dict.")
        _original_type = pd.Series if isinstance(value, pd.Series) else dict
        return value.to_dict() if isinstance(value, pd.Series) else value

    def get_values_by_key_name(self, key_name: str):
        return get_values_in_object_by_key(self.data, key_name)

    @property
    def convert_to_original(self):
        return (
            pd.Series(data=self.data) if self._original_type == pd.Series else self.data
        )


class SentenceWizard(BaseModel):
    """
    A reference to a scraper endpoint in SalesScrapers and a Copyfactory premiseURL.
    """

    scraper_name: str | None = Field(
        description="This is the endpoint from sales-scrapers", example="get-case-study"
    )
    premise_url: AnyUrl = Field(
        description="The Copyfactory premise URL you want to use. "
        "The ID is extracted from the URL",
        default=None,
    )
    premise_id: int = Field(
        description="The Copyfactory premise ID you want to use.", default=None
    )
    fallback_template: str = ""
    scraper_mapping: dict = Field(
        description="A mapping where the keys are your column "
        "names and the values are the target parameter "
        "name for SalesScrapers.",
        default={},
    )
    copyfactory_mapping: dict = Field(
        description="A mapping where the keys are your column names and the "
        "values are the target variable name you want to send to Copyfactory.",
        default={},
    )
    field_processors: dict = Field(
        description="A list of fields to validate before "
        "doing Copyfactory request."
        "If any of the fields fail validation "
        "Copyfactory will not be called.",
        default={},
    )
    restrict_to_scraped_data: bool = Field(
        description="A boolean to indicate what data the "
        "wizard is allowed to look at before calling Copyfactory."
        " defaults to only looking at the latest scrape attempt. If set to False will "
        "look at all scraped data on the row.",
        default=True,
    )
    added_key_names: set = Field(
        description="A list of keys that were added during the scraping.", default=set()
    )
    allowed_technology_categories: list = []

    @validator("premise_url")
    def validate_premise_url(cls, url):
        if not isinstance(url, str):
            return url
        return url if url.endswith("/") else f"{url}/"

    @validator("scraper_name")
    def validate_scraper_name(cls, value):
        if value is None:
            return value
        if not SETTINGS.ALLOWED_SCRAPER_NAMES:
            return value
        if value not in SETTINGS.ALLOWED_SCRAPER_NAMES:
            raise ValueError(
                f"{value} is not an allowed scraper name "
                f"your configured scrapers are {SETTINGS.ALLOWED_SCRAPER_NAMES}."
            )
        return value

    @property
    def is_premise_url_valid(self) -> bool:
        return is_valid_premise_url(self.premise_url)

    def fill_fallback(self, row: DataRow) -> str:
        """
        Fills in the template with row data.
        either returns the filled in template or an empty string.
        """
        list_pot_keys = re.findall(r"\{(.*?)\}", self.fallback_template)
        copy_of_template = self.fallback_template
        for key in list_pot_keys:
            if value := get_values_in_object_by_key(row.data, key):
                copy_of_template = copy_of_template.replace("{" + key + "}", value[0])
            else:
                return ""
        return copy_of_template

    async def run_sales_scraper(self, row: DataRow, col_prefix: str, overwrite=False):
        """
        Runs the scraping and extends the row by adding
        the column name + scraper as a prefix to ensure uniqueness.
        """
        if not self.scraper_name:
            return row
        if not self.scraper_mapping and SETTINGS.SCRAPER_MAPPING:
            self.scraper_mapping = SETTINGS.SCRAPER_MAPPING

        data = (
            replace_keys_in_object(row.data, self.scraper_mapping)
            if self.scraper_mapping
            else row.data
        )
        if scrape := await make_sales_scraper_request(self.scraper_name, data=data):
            for key, value in scrape.items():
                if key in row.data and not overwrite:
                    continue
                # Remove output schema since don't want
                # to pass schema values to Copyfactory
                # Scope scraper info to a prefixed keyname
                # to not have conflict with other scraped values.
                if key == "scraper_info" and isinstance(value, dict):
                    value = {
                        f"{SALES_SCRAPER_KEY_PREFIX_NAME}__{k}": v
                        for k, v in value.items()
                    }
                value = delete_key_in_object(
                    value, f"{SALES_SCRAPER_KEY_PREFIX_NAME}__output_schema"
                )
                # Handle technology categories to be dropped
                if self.allowed_technology_categories and isinstance(value, dict):
                    if result := get_values_in_object_by_key(
                        value, "site_technologies"
                    ):
                        for item in result:
                            if not isinstance(item, dict):
                                continue
                            for tech_name, tech_info in item.copy().items():
                                categories = tech_info.get("categories", [])
                                if all(
                                    cat not in self.allowed_technology_categories
                                    for cat in categories
                                ):
                                    delete_key_in_object(item, tech_name)

                unique_key = f"{col_prefix}__{self.scraper_name}__{key}"
                row.data[unique_key] = value
                self.added_key_names.add(unique_key)
            return row
        return row

    async def run_copyfactory(
        self,
        row: DataRow,
        content_col_name: str,
        source_col_name: str,
        keys_to_delete: set = None,
    ):
        """
        Runs Copyfactory using the current row Data.
        If successfully called with Copyfactory returns True to stop iteration
        for that datapoint.
        """
        keys_to_delete = keys_to_delete or set()
        if not self.premise_url and not self.premise_id:
            return row, False
        if self.premise_url and self.is_premise_url_valid:
            self.premise_id = get_id_from_url(self.premise_url)
        if not self.copyfactory_mapping and SETTINGS.COPYFACTORY_MAPPING:
            self.copyfactory_mapping = SETTINGS.COPYFACTORY_MAPPING

        row, is_valid = self.run_processors(row)
        if not is_valid:
            return row, False

        data = (
            replace_keys_in_object(row.data, self.copyfactory_mapping)
            if self.copyfactory_mapping
            else row.data
        )
        # Remove all other scraped data keys
        # from the row from consideration in the event of
        # multiple keys from scraped data having
        # the same name to restrict the passed data to being from
        # this sentence wizard scrape.
        if self.restrict_to_scraped_data:
            for key in keys_to_delete:
                if not key.startswith(f"{content_col_name}__{self.scraper_name}"):
                    data = delete_key_in_object(data, key)

        if cf := await make_copyfactory_request(self.premise_id, variables=data):
            row.data[content_col_name] = cf["content"]
            source = row.data.get(
                f"{content_col_name}__{self.scraper_name}__scraper_info", {}
            ).get(f"{SALES_SCRAPER_KEY_PREFIX_NAME}__data_source", "-")
            row.data[source_col_name] = f"{self.scraper_name}, {source}"
            return row, True
        return row, False

    def run_processors(self, row) -> tuple[DataRow, bool]:
        """
        Iterate over field processors and break if any don't satisfy.
        """

        if not self.field_processors:
            return row, True

        from contact_magic.preprocessors import processors

        for key, processor in self.field_processors.items():
            if item := get_values_in_object_by_key(row.data, key):
                if validation_model := processors.get(
                    processor.get("type", None), None
                ):
                    # If Pydantic fails validation/init just move on.
                    try:
                        value, is_value_valid = validation_model(
                            processor=processor,
                            value=item[0],
                            wizard=self,
                            row_data=row.data,
                        ).process()
                        row.data = replace_values_in_object(row.data, key, value)
                    except Exception:
                        is_value_valid = False
                    if not is_value_valid:
                        return row, False
        return row, True

    async def execute(
        self,
        row: DataRow,
        content_col_name: str,
        source_col_name: str,
        keys_to_delete: set = None,
    ) -> tuple[DataRow, bool]:
        """
        Executes the scraper and extends the DataRow as it moves along to
        allow for exploding the DF with more
        datapoints from the scraping + personalization.
        """
        keys_to_delete = keys_to_delete or set()
        if self.scraper_name == "FALLBACK" and self.fallback_template:
            row.data[content_col_name] = self.fill_fallback(row)
            row.data[source_col_name] = "-"
            return row, row.data[content_col_name] != ""
        row = await self.run_sales_scraper(row, col_prefix=content_col_name)
        row, success = await self.run_copyfactory(
            row, content_col_name, source_col_name, keys_to_delete=keys_to_delete
        )
        return row, success

    def __init__(self, **data: Any):
        if data.get("scraper_name", None):
            if default_options := SETTINGS.SENTENCE_WIZARD_OPTIONS.get(
                data.get("scraper_name"), None
            ):
                data |= default_options
        super().__init__(**data)


class DataPoint(BaseModel):
    """
    A reference to a datapoint to create for a given contact
    targeting a column and a list of allowed scrapers.
    """

    col_name: str = Field(
        description="The column name you want for the datapoint.",
        example="Personalization1",
    )
    sentence_wizards: list[SentenceWizard]
    keys_added: set = set()
    successful_scraper_name: str = ""

    @property
    def has_successful_sentence(self):
        return len(self.successful_scraper_name) > 0

    @property
    def get_col_name_as_source(self) -> str:
        return f"source__{self.col_name}"

    async def build_datapoint(
        self, row: DataRow, keys_to_delete: set = None, wizards_to_remove: set = None
    ):
        keys_to_delete = keys_to_delete or set()
        if wizards_to_remove := wizards_to_remove or set():
            wizards = [
                wizard
                for wizard in self.sentence_wizards
                if wizard.scraper_name not in wizards_to_remove
            ]
        else:
            wizards = self.sentence_wizards
        # remove any wizards for this row that have been used.
        for scraper in wizards:
            logger.info(
                "processing_row",
                row_number=row.index,
                scraper_name=scraper.scraper_name,
                premise_id=scraper.premise_id or get_id_from_url(scraper.premise_url),
                column_name=self.col_name,
                status="STARTING",
            )
            row, did_succeed = await scraper.execute(
                row,
                self.col_name,
                self.get_col_name_as_source,
                keys_to_delete=keys_to_delete | self.keys_added,
            )
            for key in scraper.added_key_names:
                self.keys_added.add(key)
            if did_succeed:
                if scraper.scraper_name != "FALLBACK":
                    self.successful_scraper_name = scraper.scraper_name
                logger.info(
                    "processing_row",
                    row_number=row.index,
                    scraper_name=scraper.scraper_name,
                    premise_id=scraper.premise_id
                    or get_id_from_url(scraper.premise_url),
                    column_name=self.col_name,
                    status="SUCCESS",
                )
                break
            else:
                logger.info(
                    "processing_row",
                    row_number=row.index,
                    scraper_name=scraper.scraper_name,
                    premise_id=scraper.premise_id
                    or get_id_from_url(scraper.premise_url),
                    column_name=self.col_name,
                    status="FAILED",
                )
        return row


class PersonalizationSettings(BaseModel):
    """
    A reference to a list of datapoints to generate for a given contact.
    """

    name: str = ""
    datapoints: list[DataPoint]
    uid: UUID = Field(default_factory=uuid4)
    merge_technologies: bool = True
    allowed_technology_categories: list = []
    _added_column_names: list = []
    created: datetime = Field(default_factory=datetime.utcnow)
    row_callback: List[
        Union[
            Callable[[DataRow, "PersonalizationSettings"], DataRow],
            Callable[[], Coroutine[None, None, DataRow]],
        ]
    ] = []
    campaign_meta_data: dict = Field(
        default={},
        description="A placeholder for you to add any campaign meta data. "
        "This field is not touched by any ContactMagic process.",
    )

    @validator("allowed_technology_categories", always=True)
    def validate_technologies(cls, value: list):
        if not value:
            return DEFAULT_TRACKABLE_CATEGORIES
        for tech in value:
            if tech not in ALL_CATEGORIES:
                value.remove(tech)
        return value

    @validator("datapoints")
    def validate_datapoints(cls, datapoints):
        seen_names = {}
        for dp in datapoints:
            if dp.col_name in seen_names:
                seen_names[dp.col_name] += 1
                dp.col_name = f"{dp.col_name}__{seen_names[dp.col_name]}"
            else:
                seen_names[dp.col_name] = 1
        return datapoints

    @property
    def get_datapoint_column_names(self) -> list:
        """
        Returns a list of column names and a source field.
        """
        return [dp.col_name for dp in self.datapoints] + [
            dp.get_col_name_as_source for dp in self.datapoints
        ]

    def extend_dataframe_with_settings_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(
            **{
                c: np.nan
                for c in self.get_datapoint_column_names
                if c not in df.columns
            }
        )

    def process_from_dataframe(
        self, df: pd.DataFrame, exclude_filter_func: callable = None
    ):
        """
        Process a dataframe and extend it's rows based on the
        personalization settings.
        Also accepts a callable which takes as its only argument
        the row from the dataframe to filter on.
        This function must resolve to a boolean and rows that are
        True are not processed.
        """
        df = self.extend_dataframe_with_settings_columns(df)
        untouched_rows = []
        jobs = []
        # Set to 1 based index for logging
        df.index = df.index + 1
        for i, row in df.iterrows():
            if exclude_filter_func and exclude_filter_func(row):
                untouched_rows.append(DataRow(data=row, index=i))
                continue
            jobs.append(DataRow(data=row, index=i))
        data = [
            row.convert_to_original
            for row in sorted(
                untouched_rows + self.process_data_rows(jobs),
                key=lambda dp: dp.index,
            )
        ]
        columns = df.columns.tolist()
        for new_col in self._added_column_names:
            if new_col not in columns:
                columns.append(new_col)

        return pd.DataFrame(data=data, columns=columns)

    def process_data_rows(self, data: list[DataRow]) -> list[DataRow]:
        """
        Process DataRows async.
        :param data:
        :return:
        """
        # Set the wizards scope of technology categories
        for dp in self.datapoints:
            for wizard in dp.sentence_wizards:
                wizard.allowed_technology_categories = (
                    self.allowed_technology_categories
                )
        return asyncio.run(
            do_bulk(
                [(self.build_row, {"row": row}) for row in data],
                max_workers=SETTINGS.MAX_WORKERS,
            )
        )

    def collect_technologies(self, row: DataRow) -> dict:
        category_technologies = {}
        if meta_extractions := get_values_in_object_by_key(row.data, "meta_extraction"):
            for meta_data in meta_extractions:
                if not meta_data.get("site_technologies") or not isinstance(
                    meta_data.get("site_technologies"), dict
                ):
                    continue
                for tech_name, tech_info in meta_data.get("site_technologies").items():
                    categories = tech_info["categories"]
                    for category in categories:
                        if category not in self.allowed_technology_categories:
                            continue
                        clean_category_name = category.replace(" ", "_").lower()
                        clean_dict_key = f"technology__{clean_category_name}"
                        if clean_dict_key not in category_technologies:
                            category_technologies[clean_dict_key] = []
                        category_technologies[clean_dict_key].append(tech_name)
                        if clean_dict_key not in self._added_column_names:
                            self._added_column_names.append(clean_dict_key)
        if not category_technologies:
            return category_technologies
        return {
            k: ", ".join(v).strip(",").strip() for k, v in category_technologies.items()
        }

    async def build_row(self, row: DataRow):
        """
        Iterate over all personalization datapoints and their
        allowed scrapers to extend a row of contact data
        with enrichment and personalized sentences.
        """
        keys_to_delete = set()
        wizards_to_remove = set()

        for datapoint in self.datapoints:
            row = await datapoint.build_datapoint(
                row, keys_to_delete=keys_to_delete, wizards_to_remove=wizards_to_remove
            )
            if (
                SETTINGS.ENABLE_SCRAPER_REUSE is False
                and datapoint.has_successful_sentence
            ):
                wizards_to_remove.add(datapoint.successful_scraper_name)
            for key in datapoint.keys_added:
                keys_to_delete.add(key)
        if self.merge_technologies:
            try:
                tech = self.collect_technologies(row=row)
            except Exception as e:
                logger.error(
                    "technology_collection_error",
                    index=row.index,
                    msg="Error collecting technologies",
                    error=e,
                )
                tech = {}
            row.data = row.data | tech
        if self.row_callback:
            for callback in self.row_callback:
                if isinstance(callback, Callable):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            row = await callback(row, self)
                        else:
                            row = callback(row, self)
                    except Exception as e:
                        logger.error(
                            "callback_error",
                            message=e,
                            index=row.index,
                            callback_name=callback.__name__,
                        )
        return row
