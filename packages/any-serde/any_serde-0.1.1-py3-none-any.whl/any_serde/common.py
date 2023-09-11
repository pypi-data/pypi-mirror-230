from typing import Union, TypeVar


JSON_PRIMITIVE_TYPES = [
    str,
    int,
    float,
    bool,
    None,
    type(None),
]
JSONPrimitive = Union[
    str,
    int,
    float,
    bool,
    None,
]
JSON = Union[
    JSONPrimitive,
    dict[str, "JSON"],
    list["JSON"],
]


T_Any = TypeVar("T_Any")


def resolve_newtypes(typ: type[T_Any]) -> type[T_Any]:
    # https://github.com/python/mypy/issues/3325
    while hasattr(typ, "__supertype__"):
        typ = getattr(typ, "__supertype__")
    return typ


class InvalidDeserializationException(Exception):
    """Indicates that the given data is not valid for the target type given."""


class InvalidSerializationException(Exception):
    """Indicates that the given variable could not be serialized."""
