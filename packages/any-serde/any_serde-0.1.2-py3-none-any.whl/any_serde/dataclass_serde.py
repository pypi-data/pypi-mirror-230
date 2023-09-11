""" A Serializable Dataclass Implementation """
from __future__ import annotations

import dataclasses
from functools import lru_cache
from typing import Any, TypeVar, get_type_hints
from any_serde.common import (
    JSON,
    InvalidDeserializationException,
)


T_Dataclass = TypeVar("T_Dataclass")


def is_dataclass_type(typ: Any) -> bool:
    return isinstance(typ, type) and dataclasses.is_dataclass(typ)


@lru_cache(maxsize=None)
def _get_type_hints(typ: type[object]) -> dict[str, type[Any]]:
    return get_type_hints(typ)


def _field_is_required(field: dataclasses.Field) -> bool:
    if not isinstance(field.default, dataclasses._MISSING_TYPE):
        return False

    if not isinstance(field.default_factory, dataclasses._MISSING_TYPE):
        return False

    return True


def from_data(type_: type[T_Dataclass], data: JSON) -> T_Dataclass:
    if not isinstance(data, dict):
        raise InvalidDeserializationException(f"Dataclasses serialize to dict. Got {type(data)} instead!")

    assert is_dataclass_type(type_), "Can only call dataclass_serde.from_data on dataclass types!"

    field_types = _get_type_hints(type_)  # type: ignore
    dataclass_fields = {x.name: x for x in dataclasses.fields(type_)}  # type: ignore

    fields_without_types = set(dataclass_fields) - set(field_types)
    assert not fields_without_types, f"Fields without types: {fields_without_types}"

    data_without_fields = set(data) - set(dataclass_fields)
    assert not data_without_fields, f"Data keys without fields: {data_without_fields}"

    required_field_names = [field_name for field_name, field in dataclass_fields.items() if _field_is_required(field)]

    missing_required_fields = set(required_field_names) - set(data)
    if missing_required_fields:
        raise InvalidDeserializationException(f"Data is missing required fields: {missing_required_fields}")

    from any_serde import serde

    casted_data = {
        field_name: serde.from_data(field_types[field_name], field_data) for field_name, field_data in data.items()
    }

    return type_(**casted_data)


def to_data(item: object) -> JSON:
    type_ = type(item)

    assert is_dataclass_type(type_), "Can only call dataclass_serde.to_data on dataclass instances!"

    field_types = _get_type_hints(type_)  # type: ignore
    dataclass_fields = {x.name: x for x in dataclasses.fields(type_)}  # type: ignore

    fields_without_types = set(dataclass_fields) - set(field_types)
    assert not fields_without_types, f"Fields without types: {fields_without_types}"

    from any_serde import serde

    return {
        field_name: serde.to_data(field_types[field_name], getattr(item, field_name)) for field_name in dataclass_fields
    }
