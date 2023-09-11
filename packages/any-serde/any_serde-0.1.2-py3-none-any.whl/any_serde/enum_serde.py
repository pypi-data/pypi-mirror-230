from enum import Enum
from typing import TypeVar, Any
from any_serde.common import InvalidDeserializationException, JSON

T_Enum = TypeVar("T_Enum", bound=Enum)


def is_enum_type(typ: Any) -> bool:
    return isinstance(typ, type) and issubclass(typ, Enum)


def from_data(type_: type[T_Enum], data: JSON) -> T_Enum:
    if not isinstance(data, str):
        raise InvalidDeserializationException(f"Enums serialize to strings. Got {type(data)} instead!")

    split_items = data.split(".")

    if len(split_items) != 2:
        raise InvalidDeserializationException(f"Serialized enums are EnumType.ENUM_VALUE. Got {data} instead!")

    enum_type_str, enum_value_str = split_items

    enum_value = type_[enum_value_str]

    if not data == str(enum_value):
        raise InvalidDeserializationException(f"Wrong Enum type? Expected {type_}, got {enum_type_str}!")

    return enum_value


def to_data(enum_value: Enum) -> str:
    return str(enum_value)
