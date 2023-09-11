import types
from typing import (
    Any,
    Literal,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from any_serde.common import (
    InvalidSerializationException,
    InvalidDeserializationException,
    JSON,
    resolve_newtypes,
)
from any_serde import enum_serde, primitives_serde, dataclass_serde, union_serde


T_Any = TypeVar("T_Any")


def from_data(
    type_: type[T_Any],
    data: JSON,
) -> T_Any:
    """Constructs a python variable of the given type from JSON data.

    Args:
        _type: The type of the variable to construct. E.g. list[int] or (Set[str] | None)
        data: The JSON data to deserialize
    """
    type_ = resolve_newtypes(type_)

    if primitives_serde.is_primitive_type(type_):
        return primitives_serde.from_data(type_, data)  # type: ignore

    if enum_serde.is_enum_type(type_):
        return enum_serde.from_data(type_, data)  # type: ignore

    if dataclass_serde.is_dataclass_type(type_):
        return dataclass_serde.from_data(type_, data)

    type_origin_nullable = get_origin(type_)
    if type_origin_nullable is None:
        raise TypeError(f"Unsupported type: {type_}")

    type_origin = resolve_newtypes(type_origin_nullable)
    type_args = [resolve_newtypes(type_arg) for type_arg in get_args(type_)]

    if type_origin in (Union, types.UnionType):
        return union_serde.from_data(type_, data)

    if type_origin in (list, set):
        if not isinstance(data, list):
            raise InvalidDeserializationException(
                f"{type_origin} objects serialize to lists. Got {type(data)} instead!"
            )

        assert len(type_args) == 1
        list_item_type = type_args[0]

        return type_origin(
            (from_data(list_item_type, list_item) for list_item in data),
        )

    if type_origin is dict:
        if not isinstance(data, dict):
            raise InvalidDeserializationException(f"Dict objects serialize to dicts. Got {type(data)} instead!")

        assert len(type_args) == 2

        key_type, value_type = type_args

        return {from_data(key_type, key): from_data(value_type, value) for key, value in data.items()}  # type: ignore

    if type_origin is tuple:
        assert type_args

        if not isinstance(data, list):
            raise InvalidDeserializationException(f"Tuple objects serialize to lists. Got {type(data)} instead!")

        if len(data) != len(type_args):
            raise InvalidDeserializationException(
                f"Tuple type length {len(type_args)} does not match data length {len(data)}!"
            )

        return tuple(  # type: ignore
            from_data(tuple_item_type, tuple_item) for tuple_item_type, tuple_item in zip(type_args, data)
        )

    if type_origin is Literal:
        assert type_args

        if len(type_args) > 1:
            return from_data(
                Union[  # type: ignore
                    tuple(Literal[type_arg] for type_arg in type_args)  # type: ignore
                ],
                data,
            )

        literal_value = type_args[0]

        # TODO: figure out how to pass serialization options
        item = from_data(type(literal_value), data)

        assert type(item) == type(literal_value)

        if item != literal_value:
            raise InvalidSerializationException("Deserialized value does not match Literal type!")

        return item  # type: ignore

    raise NotImplementedError(f"Unsupported type_origin: {type_origin}")


def to_data(type_: Type[T_Any], item: T_Any) -> JSON:
    """Converts a python variable to JSON data.

    Args:
        type_: The intended type of item
        item: The python variable to serialize
    """
    type_ = resolve_newtypes(type_)

    if primitives_serde.is_primitive_type(type_):
        # TODO check type matches item
        return primitives_serde.to_data(item)  # type: ignore

    if enum_serde.is_enum_type(type_):
        return enum_serde.to_data(item)  # type: ignore

    if dataclass_serde.is_dataclass_type(type_):
        if type(item) is not type_:
            raise InvalidSerializationException(f"Specified type_ {type_} does not match item type {type(item)}!")
        return dataclass_serde.to_data(item)  # type: ignore

    type_origin_nullable = get_origin(type_)
    if type_origin_nullable is None:
        raise InvalidSerializationException(f"Unsupported type: {type_}")

    type_origin = resolve_newtypes(type_origin_nullable)
    type_args = [resolve_newtypes(type_arg) for type_arg in get_args(type_)]

    if type_origin in (Union, types.UnionType):
        return union_serde.to_data(type_, item)

    if type_origin in (list, set):
        if not isinstance(item, type_origin):
            raise InvalidSerializationException(f"Specified type_ {type_} does not match item type {type(item)}!")

        assert len(type_args) == 1
        list_item_type = type_args[0]

        return type_origin(
            (to_data(list_item_type, list_item) for list_item in item),
        )

    if type_origin is dict:
        if not isinstance(item, dict):
            raise InvalidSerializationException(f"Specified type_ {type_} does not match item type {type(item)}!")

        assert len(type_args) == 2

        key_type, value_type = type_args

        data: dict[str, Any] = {}

        for key, value in item.items():
            key_data = to_data(key_type, key)
            if not isinstance(key_data, str):
                raise InvalidSerializationException(
                    f"Dict keys must serialize to strings. Got {type(key_data)} instead!"
                )
            value_data = to_data(value_type, value)
            data[key_data] = value_data

        return data

    if type_origin is tuple:
        assert type_args
        if not isinstance(item, tuple):
            raise InvalidSerializationException(f"Specified type_ {type_} does not match item type {type(item)}!")

        if len(item) != len(type_args):
            raise InvalidSerializationException(
                f"Specified type {type_} has length {len(type_args)} but item has {len(item)}!"
            )

        return [to_data(tuple_item_type, tuple_item) for tuple_item_type, tuple_item in zip(type_args, item)]

    if type_origin is Literal:
        assert type_args

        if len(type_args) > 1:
            return to_data(
                Union[  # type: ignore
                    tuple(Literal[type_arg] for type_arg in type_args)  # type: ignore
                ],
                item,
            )

        literal_value = type_args[0]

        if type(item) != type(literal_value):
            raise InvalidSerializationException(
                f"Item type {type(item)} does not match literal type {type(literal_value)}!"
            )

        if item != literal_value:
            raise InvalidSerializationException(f"Item {item} does not match literal value {literal_value}!")

        return to_data(type(literal_value), item)

    raise NotImplementedError(f"Unsupported type_origin: {type_origin}")
