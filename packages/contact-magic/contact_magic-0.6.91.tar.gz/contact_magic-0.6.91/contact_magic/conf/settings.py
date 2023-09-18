"""
Config file that reads from .env file and parses based on type set.

https://docs.pydantic.dev/usage/settings/
"""
from urllib.parse import urlparse

import pytz
import requests
from pydantic import AnyUrl, BaseSettings, Field, validate_model, validator


class BaseConfig(BaseSettings):
    """
    Settings for project.
    """

    COPYFACTORY_API_KEY: str = Field(
        description="The Copyfactory global API key.", default=None
    )
    SALES_SCRAPERS_API_KEY: str = Field(
        description="The SalesScrapers API key", default=None
    )
    MASTERSHEET_URL: AnyUrl = Field(
        description="The URL pointing to your agency mastersheet.", default=None
    )
    GOOGLE_PROJECT_ID: str = Field(
        description="Google projectID from auth file.", default=None
    )
    GOOGLE_PRIVATE_KEY_ID: str = Field(
        description="Google PrivateKeyId from auth file.", default=None
    )
    GOOGLE_PRIVATE_KEY: str = Field(
        description="Google PrivateKey from auth file.", default=None
    )
    GOOGLE_CLIENT_ID: str = Field(
        description="Google client ID from auth file.", default=None
    )
    GOOGLE_CLIENT_EMAIL: str = Field(
        description="Google client Email from auth file.", default=None
    )
    TIMEZONE: str = Field(
        description="A valid Pytz timezone.", default="America/New_York"
    )
    ALLOWED_SCRAPER_NAMES: list = Field(
        description="A list of scraper names you want to allow.", default=[]
    )
    MAX_WORKERS: int = Field(
        description="The number of concurrent rows you want to process,"
        " this should not be higher than your "
        "concurrency limit from your proxy provider.",
        default=5,
    )
    DATA_CHUNK_SIZE: int = Field(
        default=200,
        description="The number of rows to process "
        "at once in any of the 'process' methods.",
    )
    SCRAPER_MAPPING: dict = Field(
        description="Mapping where the keys are field names "
        "in your data and the values are what you want to swap it with.",
        default={},
    )
    COPYFACTORY_MAPPING: dict = Field(
        description="Mapping where the keys are field names "
        "in your data and the values are what you want to swap it with.",
        default={},
    )
    SENTENCE_WIZARD_OPTIONS: dict = Field(
        description="Mapping where the keys are the scraper names "
        "and the values are a dict of additional scraper options to pass.",
        default={},
    )
    ENABLE_SCRAPER_REUSE: bool = Field(
        description="This setting determines whether a contact can "
        "have multiple personalized sentences from the same scraper.",
        default=False,
    )
    WEBHOOK_URL: AnyUrl = Field(
        description="A webhook endpoint to be notified of events.", default=None
    )

    @validator("TIMEZONE")
    def validate_timezone(cls, value):
        timezones = pytz.all_timezones_set
        if value not in timezones:
            value = "America/New_York"
        return value

    @validator("MASTERSHEET_URL")
    def validate_mastersheet(cls, url):
        if not url:
            return url
        if not isinstance(url, str):
            raise ValueError("Mastersheet is not a valid spreadsheet.")
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            raise ValueError("Mastersheet is not a valid spreadsheet.")
        if parsed_url.netloc != "docs.google.com":
            raise ValueError("Mastersheet is not a valid spreadsheet.")
        if "spreadsheets" not in parsed_url.path:
            raise ValueError("Mastersheet is not a valid spreadsheet.")
        return url

    @property
    def GOOGLE_CONFIG(self) -> dict:
        """
        Returns a valid Google dict for authentication or empty dict.
        :return:
        """
        if not all(
            (
                self.GOOGLE_PROJECT_ID,
                self.GOOGLE_PRIVATE_KEY_ID,
                self.GOOGLE_PRIVATE_KEY,
                self.GOOGLE_CLIENT_ID,
                self.GOOGLE_CLIENT_EMAIL,
            )
        ):
            return {}
        return {
            "type": "service_account",
            "project_id": self.GOOGLE_PROJECT_ID,
            "private_key_id": self.GOOGLE_PRIVATE_KEY_ID,
            "private_key": self.GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": self.GOOGLE_CLIENT_EMAIL,
            "client_id": self.GOOGLE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/"
            f"robot/v1/metadata/x509/{self.GOOGLE_CLIENT_EMAIL}",
        }

    def update_settings(self, new_settings: dict = None, env_file_path: str = None):
        """
        Update contact magic config through either a dict or a env file path.
        """
        new_settings = new_settings or {}
        if env_file_path:
            parsed_values = BaseConfig(_env_file=env_file_path).dict()
            new_settings = parsed_values | new_settings
        if not isinstance(new_settings, dict):
            return self
        for k, v in {
            k: v for k, v in new_settings.items() if k in self.__fields__.keys()
        }.items():
            self.__setattr__(k, v)
        *_, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error
        return self

    def notify_webhook(self, event_name: str, data: dict):
        if self.WEBHOOK_URL:
            requests.post(self.WEBHOOK_URL, json={"event": event_name, "data": data})

    class Config:
        validate_assignment = True
        env_file = ".env"
        env_file_encoding = "utf-8"


SETTINGS = BaseConfig()
