import collections
import functools
import sys

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import litecore.serialization.asjson.exceptions as exc

JSONType = Union[Dict[str, Any], List, str, int, float]

SERIALIZATION_MARKER = '__pythonclass__'
DATA_MARKER = '__data__'
METADATA_MARKER = '__metadata__'
MODULE_KEY = '__module__'
CLASS_KEY = '__qualname__'


def class_info(class_obj: Type) -> Dict[str, Any]:
    try:
        return {
            MODULE_KEY: class_obj.__module__,
            CLASS_KEY: class_obj.__qualname__,
        }
    except Exception as err:
        msg = f'could not get module and name for {class_obj!r}'
        raise exc.JSONSerializationTypeError(msg) from err


def get_class_object(info: Dict[str, Any]):
    try:
        module = sys.modules.get(info[MODULE_KEY])
        return getattr(module, info[CLASS_KEY])
    except Exception as err:
        msg = (
            f'could not resolve reference for class '
            f'{info[MODULE_KEY]}.{info[CLASS_KEY]}'
        )
        raise exc.JSONDeserializationError(msg) from err


def marker(
        obj: Any,
        data: Any,
        *,
        metadata_key: str = METADATA_MARKER,
        metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    result = {
        SERIALIZATION_MARKER: class_info(type(obj)),
        DATA_MARKER: data,
    }
    if metadata is not None:
        result[metadata_key] = metadata
    return result


_decoders = {}


def register_decoder(class_obj: Type) -> Callable:
    """Function decorator to register a JSON decoder."""
    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        if class_obj in _decoders:
            dupe = _decoders[class_obj]
            msg = (
                f'attempt to insert decoder {func!r} for {class_obj!r}'
                f'duplicates existing decoder {dupe!r}'
            )
            raise exc.JSONRuntimeError(msg)
        _decoders[class_obj] = func
        return func
    return decorator


@functools.singledispatch
def encode(obj) -> Any:
    """Encode objects of various types to JSON."""
    msg = f'unrecognized type {type(obj)} object {obj!r}'
    raise exc.JSONSerializationTypeError(msg)


def decode(data: JSONType) -> Any:
    if not isinstance(data, collections.abc.Mapping):
        return data
    class_info = data.get(SERIALIZATION_MARKER)
    if class_info is None:
        return data
    class_obj = get_class_object(class_info)
    decoder = _decoders.get(class_obj)
    if decoder is None:
        msg = f'no registered JSON decoder for {class_obj!r}'
        raise exc.JSONDeserializationError(msg)
    try:
        return decoder(data[DATA_MARKER])
    except Exception as err:
        msg = f'could not deserialize JSON data {data!r}'
        raise exc.JSONDeserializationError(msg) from err


class PairDecoder:
    def __init__(self, *, hook: Optional[Callable] = None):
        self.hook = hook

    def __repr__(self):
        return f'{type(self).__qualname__}(hook={self.hook!r})'

    def __call__(self, data: List[Tuple[str, Any]]):
        if isinstance(data, collections.abc.Mapping):
            keys = set(key for key, value in data.items())
        else:
            keys = set(key for key, value in data)
        if SERIALIZATION_MARKER in keys:
            return decode(dict(data))
        return self.hook(data) if self.hook is not None else data


decode_ordered = PairDecoder(hook=collections.OrderedDict)
