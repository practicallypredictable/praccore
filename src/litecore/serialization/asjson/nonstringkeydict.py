import collections
import types

from typing import (
    Any,
    Dict,
    Hashable,
    Iterator,
    List,
    Mapping,
    Sequence,
    Tuple,
)

import litecore.serialization.asjson.coding as coding

NONSTRING_KEY_PREFIX = '__nonstringkey_'
ORIGINAL_KEY_PREFIX = '__orig_key__'
ORIGINAL_VALUE_PREFIX = '__orig_value__'


def _change(key: Hashable, value: Any, index: int) -> Tuple[str, Any]:
    if isinstance(key, str):
        return (key, value)
    else:
        return (
            f'{NONSTRING_KEY_PREFIX}{index}__',
            {ORIGINAL_KEY_PREFIX: key, ORIGINAL_VALUE_PREFIX: value},
        )


def _change_back(key: str, value: Any) -> Dict[Hashable, Any]:
    if key.startswith(NONSTRING_KEY_PREFIX):
        return (value[ORIGINAL_KEY_PREFIX], value[ORIGINAL_VALUE_PREFIX])
    else:
        return (key, value)


class NonStringKeyMappingProxy(collections.abc.Mapping):
    __slots__ = ('data',)

    def __init__(self, mapping: Mapping[Hashable, Any]):
        self.data = types.MappingProxyType(mapping)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def encoded_items(self) -> Iterator[Tuple[str, Any]]:
        for index, (key, value) in enumerate(self.data.items()):
            yield _change(key, value, index)


def _decoded_items(
        mapping: Mapping[str, Any],
) -> Iterator[Tuple[Hashable, Any]]:
    for key, value in mapping.items():
        yield _change_back(key, value)


@coding.encode.register(NonStringKeyMappingProxy)
def _encode_nonstringkey_proxy(obj):
    return coding.marker(obj, dict(obj.encoded_items()))


@coding.register_decoder(NonStringKeyMappingProxy)
def _decode_nonstringkey_proxy(
        data: Dict[str, Any]) -> Dict[Hashable, Any]:
    return dict(_decoded_items(data))


class NonStringKeyMappingProxySequence(collections.abc.Sequence):
    __slots__ = ('data',)

    def __init__(self, sequence: Sequence[Mapping[Hashable, Any]]):
        self.data = [
            types.MappingProxyType(mapping)
            for mapping in sequence
        ]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index_or_slice):
        return self.data[index_or_slice]

    def encoded_items(self) -> Iterator[Dict[Tuple[str, Any]]]:
        for item in self.data:
            yield dict(item.encoded_items())


@coding.encode.register(NonStringKeyMappingProxySequence)
def _encode_nonstringkey_proxy_sequence(obj):
    return coding.marker(obj, list(obj.encoded_items()))


@coding.register_decoder(NonStringKeyMappingProxySequence)
def _decode_nonstringkey_proxy_sequence(
        data: Dict[str, Any]) -> List[Dict[Hashable, Any]]:
    return [dict(_decoded_items(item)) for item in data]
