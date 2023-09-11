import types
from typing import (
    Any,
    Sequence,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from any_serde.common import InvalidSerializationException, InvalidDeserializationException, JSON, resolve_newtypes


T_Any = TypeVar("T_Any")


def _get_union_args(type_: type[T_Any]) -> Sequence[type[Any]]:
    type_origin_nullable = get_origin(type_)

    assert type_origin_nullable is not None, f"Calling union serde on non-union type: {type_}"

    type_origin = resolve_newtypes(type_origin_nullable)
    type_args = [resolve_newtypes(type_arg) for type_arg in get_args(type_)]

    assert type_origin in (Union, types.UnionType), f"Calling union serde on non-union type: {type_}"

    deduped_type_args = list(set(type_args))

    return deduped_type_args


def from_data(
    type_: Type[T_Any],
    data: JSON,
) -> T_Any:
    type_args = _get_union_args(type_)

    from any_serde import serde

    for union_arg in type_args:
        try:
            return serde.from_data(union_arg, data)
        except InvalidDeserializationException:
            pass

    raise InvalidDeserializationException("Could not deserialize to any union option.")


def to_data(
    type_: type[T_Any],
    item: T_Any,
) -> JSON:
    type_args = _get_union_args(type_)

    from any_serde import serde

    for union_arg in type_args:
        try:
            return serde.to_data(union_arg, item)
        except InvalidSerializationException:
            pass

    raise InvalidSerializationException("Could not serialize from any union option.")
