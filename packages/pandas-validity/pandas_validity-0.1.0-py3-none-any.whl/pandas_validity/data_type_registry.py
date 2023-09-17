from __future__ import annotations

import pandas as pd

from pandas_validity.custom_typings import ValidationFunc_T
from pandas_validity.exceptions import RegistryError


def check_callable(_callable: ValidationFunc_T):
    if not callable(_callable):
        raise RegistryError(f"`{_callable}` should be a callable")
    test_case = int
    try:
        ret = _callable(test_case)
    except Exception as err:
        raise RegistryError(
            "Callable failed for the sanity check:"
            f" `{_callable.__name__}({test_case.__name__})`: '{err}'"
        ) from err
    if not isinstance(ret, bool):
        raise RegistryError(
            f"Callable `{_callable.__name__}` should return a boolean value - returned"
            f" `{ret}`."
        )


class DataTypeValidatorsRegistry(dict):
    def register_decorator(
        self,
        _callable: ValidationFunc_T | None = None,
        *,
        alias: type | str | None = None,
    ):
        def decorator(_callable: ValidationFunc_T) -> ValidationFunc_T:
            self.register(_callable, alias)
            return _callable

        if _callable is None:
            return decorator
        else:
            return decorator(_callable=_callable)  # type: ignore

    def register(self, _callable: ValidationFunc_T, alias: type | str | None = None):
        check_callable(_callable)
        self[_callable] = _callable
        if alias is not None:
            self[alias] = _callable
        return self

    def __getitem__(self, __key):
        try:
            return super().__getitem__(__key)
        except KeyError:
            raise RegistryError(f"'{__key}' is not registered as a valid callable.")


def build_data_type_validators_registry() -> DataTypeValidatorsRegistry:
    data_type_validators_registry = DataTypeValidatorsRegistry()
    data_type_validators_registry.register(pd.api.types.is_string_dtype, alias="str")
    data_type_validators_registry.register(pd.api.types.is_integer_dtype, alias="int")
    data_type_validators_registry.register(pd.api.types.is_float_dtype, alias="float")
    data_type_validators_registry.register(pd.api.types.is_string_dtype, alias="str")
    data_type_validators_registry.register(
        pd.api.types.is_datetime64_dtype, alias="datetime"
    )
    data_type_validators_registry.register(pd.api.types.is_bool_dtype, alias="bool")
    return data_type_validators_registry
