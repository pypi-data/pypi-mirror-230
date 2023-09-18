import re
from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.main import validate_model

from contact_magic import SentenceWizard


class BaseProcessor(BaseModel):
    """
    Base validator to inherit from. Define the 'validate' method to return a boolean.
    """

    value: Any = None
    processor: dict
    wizard: SentenceWizard
    row_data: dict

    _is_valid: bool = True

    def process(self) -> tuple[Any, bool]:
        if not self._is_valid:
            return self.value, self._is_valid
        return self.validate(**self.processor)

    @abstractmethod
    def validate(self, *args, **kwargs) -> tuple[Any, bool]:
        return self.value, self._is_valid

    class Config:
        arbitrary_types_allowed = True

        @classmethod
        def prepare_field(cls, field: ModelField) -> None:
            # Ensure any self declared validation models don't require a value.
            if field.name == "value":
                field.required = False

    def __init__(self, **data: Any) -> None:
        """
        Don't raise validation error if can't coerce,
        just set value to None which fails validation.
        """
        values, fields_set, validation_error = validate_model(self.__class__, data)
        if validation_error:
            self._is_valid = False
        super().__init__(**data)


class StringProcessor(BaseProcessor):
    value: str

    def validate(
        self,
        min_length=None,
        max_length=None,
        regex=None,
        choices=None,
        *args,
        **kwargs
    ) -> tuple[Any, bool]:
        if min_length is not None and len(self.value) < min_length:
            return self.value, False

        if max_length is not None and len(self.value) > max_length:
            return self.value, False

        if regex is not None and not bool(re.match(regex, self.value)):
            return self.value, False

        if choices is not None and self.value not in choices:
            return self.value, False
        return self.value, True


class IntegerProcessor(BaseProcessor):
    value: int

    def validate(
        self, min_amount=None, max_amount=None, *args, **kwargs
    ) -> tuple[Any, bool]:
        if min_amount is not None and self.value < min_amount:
            return self.value, False

        if max_amount is not None and self.value > max_amount:
            return self.value, False

        return self.value, True


class FloatProcessor(BaseProcessor):
    value: float

    def validate(
        self, min_amount=None, max_amount=None, *args, **kwargs
    ) -> tuple[Any, bool]:
        if min_amount is not None and self.value < min_amount:
            return self.value, False

        if max_amount is not None and self.value > max_amount:
            return self.value, False
        return self.value, True


processors = {
    "str": StringProcessor,
    "string": StringProcessor,
    "int": IntegerProcessor,
    "integer": IntegerProcessor,
    "float": FloatProcessor,
}
