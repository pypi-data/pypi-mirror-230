from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from pandas_validity.abstract import AbstractValidator
from pandas_validity.custom_typings import ValidationFunc_T
from pandas_validity.data_type_registry import (
    DataTypeValidatorsRegistry,
    build_data_type_validators_registry,
)
from pandas_validity.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DataFrameValidator(AbstractValidator):

    """
    Context manager to validate pandas dataframes.

    This class is designed to be used as a context manager for validating pandas
    dataframes. It aggregates all `ValidationError` that occur during the validation
    process and raises them collectively upon exiting the context manager.

    Upon exiting the context manager, if any of the validation methods fail,
    a `ValidationGroupError` will be raised, containing a list of individual
    `ValidationErrors`.

    Example
    --------
    df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": ["a", "b", "c"],
            "C": [2.3, 4.5, 9.2],
            "D": [
                datetime.datetime(2023, 1, 1, 1),
                datetime.datetime(2023, 1, 1, 2),
                datetime.datetime(2023, 1, 1, 3),
            ],
        }
    )
    expected_columns=list(valid_df.columns),
    data_types_mapping={
            "A": 'int',
            "B": 'str',
            "C": 'float',
        }
    with DataFrameValidator(valid_df) as validator:
        validator.is_empty()
        validator.has_required_columns(expected_columns)
        validator.has_no_redundant_columns(expected_columns)
        validator.has_valid_data_types(data_types_mapping)
        validator.has_no_missing_data()

    """

    def __init__(
        self,
        df: pd.DataFrame,
        registry: DataTypeValidatorsRegistry = build_data_type_validators_registry(),
    ) -> None:
        """Initialize the DataFrameValidator.

        Args:
            df (pd.DataFrame): The dataframe to be validated.
            registry (DataTypeValidatorsRegistry): registrydata type validators

        """
        super().__init__(logger=logger)
        self._df = df
        self._registry = registry

    def is_empty(self) -> None:
        """Check if the dataframe is empty."""
        if self._df.empty:
            self._errors.append(ValidationError("The dataframe is empty."))

    def has_required_columns(self, expected_columns: list[str]) -> None:
        """Check if the dataframe contains all required columns"""
        diff = set(expected_columns) - set(self._df.columns)
        if diff:
            self._errors.append(
                ValidationError(f"The dataframe has missing columns: {sorted(diff)}")
            )

    def has_no_redundant_columns(self, expected_columns: list[str]) -> None:
        """Check if the dataframe contains no redundant columns"""
        diff = set(self._df.columns) - set(expected_columns)
        if diff:
            self._errors.append(
                ValidationError(f"The dataframe has redundant columns: {list(diff)}")
            )

    def has_valid_data_types(
        self, expected_data_types: dict[str, ValidationFunc_T | type | str]
    ) -> None:
        """Check if columns have valid data types"""
        for col, dtype in self._df.dtypes.items():
            try:
                val = expected_data_types[str(col)]
            except KeyError:
                continue
            validator = self._registry[val]
            valid = validator(dtype)
            if not valid:
                self._errors.append(
                    ValidationError(f"Column '{col}' has invalid data-type: '{dtype}'")
                )

    def has_no_missing_data(self) -> None:
        """Check if the dataframe has no missing values."""
        missing_data_mask = self._df.isna()
        if missing_data_mask.any().any():
            res = []
            for row, col in np.argwhere(missing_data_mask):
                index = missing_data_mask.index[row]
                column = missing_data_mask.columns[col]
                value = self._df.iloc[row, col]
                res.append({"index": index, "column": column, "value": value})

            self._errors.append(
                ValidationError(f"Found {len(res)} missing values: {res}")
            )
