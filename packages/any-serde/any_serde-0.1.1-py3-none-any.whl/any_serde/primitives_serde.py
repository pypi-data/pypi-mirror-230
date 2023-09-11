from typing import TypeVar, Any

from any_serde.common import (
    JSON_PRIMITIVE_TYPES,
    JSONPrimitive,
    InvalidDeserializationException,
    JSON,
)

T_JSONPrimitive = TypeVar("T_JSONPrimitive", bound=JSONPrimitive)


def is_primitive_type(typ: Any) -> bool:
    return typ in JSON_PRIMITIVE_TYPES


def from_data(type_: type[T_JSONPrimitive], data: JSON) -> T_JSONPrimitive:
    assert is_primitive_type(type_), f"Can only call primitives_serde.from_data on primitive types! Got {type_}"

    if type_ is float and isinstance(data, int):
        return float(data)  # type: ignore

    if type_ is int and isinstance(data, float) and data % 1 == 0:
        return round(data)  # type: ignore

    if type_ is None and data is None:
        return data

    if type(data) is not type_:
        raise InvalidDeserializationException(f"Cannot deserialize {data} (type={type(data)}) to {type_}!")

    return data  # type: ignore


def to_data(item: JSONPrimitive) -> JSON:
    return item
