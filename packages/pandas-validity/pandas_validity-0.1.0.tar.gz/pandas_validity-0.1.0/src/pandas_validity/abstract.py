import abc
import logging

from pandas_validity.exceptions import ValidationErrorsGroup

logger = logging.getLogger(__name__)


class AbstractValidator(abc.ABC):
    def __init__(self, logger: logging.Logger) -> None:
        self._errors: list[Exception]
        self._logger = logger
        self.reset()

    def reset(self):
        self._errors = []

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        errors = self._errors
        self.reset()
        if exc_val is not None:
            self._logger.exception(
                f"Unexpected error occurred: ({exc_type}) {exc_val}."
            )
            errors = [*errors, exc_val]
        if errors:
            for err in errors:
                self._logger.error("Error occurred: (%s) %s", type(err), err)
            raise ValidationErrorsGroup(
                f"Validation errors found: {len(errors)}.", errors
            )
