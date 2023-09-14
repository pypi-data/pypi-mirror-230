import inspect

from enum import Enum
from pulsar_sdk_py import enums
from dataclasses import dataclass
from dacite import from_dict, Config
from pulsar_sdk_py.dataclasses.schemas import TokenChain


def get_enum_classes(module) -> list[type[Enum]]:
    return [
        obj
        for name, obj in inspect.getmembers(module)
        if inspect.isclass(obj) and issubclass(obj, Enum) and obj is not Enum
    ]


def create_enum_hook(enum_dict):
    return lambda data: enum_dict[data]


def create_enum_dict(enum_class):
    return {member.value: member for member in enum_class}


enum_classes = get_enum_classes(enums)
enum_dicts = {enum_class: create_enum_dict(enum_class) for enum_class in enum_classes}
type_hooks = {enum_class: create_enum_hook(enum_dicts[enum_class]) for enum_class in enum_classes}


def serialize_token_chain(data) -> dict[enums.ChainKeys, TokenChain]:
    return {
        enums.ChainKeys(chain): TokenChain(type=token_info["type"], value=token_info["value"])
        for chain, token_info in data.items()
    }


type_hooks[dict[enums.ChainKeys, TokenChain]] = serialize_token_chain
config = Config(type_hooks=type_hooks)


def serialize_to_dataclass(data, dataclass_to_serialize: type[dataclass]):
    return from_dict(dataclass_to_serialize, data, config)
