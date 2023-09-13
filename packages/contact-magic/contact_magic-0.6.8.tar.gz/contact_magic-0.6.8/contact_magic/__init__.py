import importlib.metadata

__version__ = importlib.metadata.version("contact-magic")

from .conf.settings import SETTINGS as settings  # noqa
from .models import DataPoint, DataRow, PersonalizationSettings, SentenceWizard  # noqa
from .scripts.agency import app as agency  # noqa
