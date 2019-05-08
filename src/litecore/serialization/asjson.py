import functools
import json
import logging

from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Mapping,
    Optional,
    Type,
)

from litecore import LitecoreError as _ErrorBase
import litecore.check
import litecore.registry
import litecore.mappings.stringkey

log = logging.getLogger(__name__)

_json_decoders = litecore.registry.StringKeyClassRegistry()

DEFAULT_CLASS_KEY = '__class__'
DEFAULT_CLASS_ID_KEY = '__identifier__'
DEFAULT_CLASS_MODULE_KEY = '__module__'
DEFAULT_CLASS_QUALNAME_KEY = '__qualname__'
DEFAULT_DATA_KEY = '__data__'
DEFAULT_METADATA_KEY = '__metadata__'
DEFAULT_KEY_MARKER = '__key__'
DEFAULT_VALUE_MARKER = '__value__'


class JSONSerializationTypeError(_ErrorBase, TypeError):
    """Could not serialize a type to JSON."""
    pass


class JSONDeserializationValueError(_ErrorBase, ValueError):
    """Could not deserialize from JSON."""
    pass


JSONEncodingType = Dict[str, Any]


def jsonify(
        obj: Any,
        *,
        make_string_key: Callable = _non_string_key,
        key_prefix: str = '__nonstring_key__',
):
    if litecore.check.is_mapping(obj):
        for key, value in obj.items():
            yield from _make_string_keys(
                key,
                value,
                _make_key=_non_string_key
                _prefix=key_prefix,
            )
    elif litecore.check.is_iterable(obj):
        for child in obj:
            yield from jsonify(child)
    else:
        yield obj


def _make_string_keys(key: Hashable, value: Any, *, _prefix: str):
    if isinstance(key, str):
        yield key, value
    else:
        key = 
        yield {'__key__': key, '__value__': jsonify(value)}


class JSONDict(litecore.mappings.stringkey.StringKeyDict):
    pass


class JSONOrderedDict(litecore.mappings.stringkey.StringKeyOrderedDict):
    pass


def decoder(key: str):
    """Function decorator to register a JSON decoder."""
    def decorator(func: Callable):
        _json_decoders.insert(func, key=key)
        return func
    return decorator


def _class_markers(name: str, **kwargs) -> JSONEncodingType:
    markers = {DEFAULT_CLASS_ID_KEY: name}
    markers.update(**kwargs)
    return markers


def _data_markers(data: Any, **kwargs) -> JSONEncodingType:
    markers = {DEFAULT_DATA_KEY: data}
    markers.update(**kwargs)
    return markers


def _metadata_markers(metadata: Mapping[str, Any], **kwargs) -> JSONEncodingType:
    markers = {DEFAULT_METADATA_KEY: metadata}
    markers.update(**kwargs)
    return markers


def add_markers(
        *,
        name: str,
        data: Any,
        metadata: Optional[Mapping[str, Any]] = None,
        class_markers: Callable = _class_markers,
        data_markers: Callable = _data_markers,
        metadata_markers: Callable = _metadata_markers,
        **kwargs
) -> JSONEncodingType:
    encoding = {}
    encoding.update(class_markers(name=name))
    encoding.update(data_markers(data=data))
    if metadata:
        encoding.update(metadata_markers(metadata=metadata))
    return encoding


@functools.singledispatch
def encode(obj):
    """Encode objects of various types to JSON.

    Decorated by functools.singledispatch to dispatch on the type of the object
    argument. See the registry property of functions decorated by
    functools.singledispatch to view the supported types and a mapping of types
    to the encoding functions.

    The generic function raises JSONSerializationTypeError to catch unrecognized types.

    """
    msg = f'Undispatched attempt to encode object {obj!r} of type {type(obj)}'
    raise JSONSerializationTypeError(msg)


class _EncoderHelper:
    def __init__(
            self,
            obj_type: Type,
            name: str,
            encoder: Callable,
            **kwargs,
    ) -> None:
        self.name = name
        self.obj_type = obj_type
        self.encoder = encoder
        self.kw = kwargs

    def __call__(self, obj):
        return add_markers(name=self.name, data=self.encoder(obj), **self.kw)

    def __repr__(self) -> str:
        r = (
            f'{type(self)}.__name__({self.name}, {self.obj_type!r}'
            f', {self.encoder}'
        )
        if self.kw:
            r += ', '.join(f'{k}={v}' for k, v in self.kw.items())
        r += ')'
        return r


class _DecoderHelper:
    def __init__(self, obj_type: Type) -> None:
        self.obj_type = obj_type

    def __call__(self, data):
        return self.obj_type(data)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.obj_type!r})'


def register_type(
        obj_type: Type,
        name: str,
        encoder: Callable,
        decoder: Optional[Callable] = None,
        **kwargs,
) -> None:
    helper = _EncoderHelper(
        obj_type,
        name,
        encoder,
        **kwargs,
    )
    encode.register(obj_type)(helper)
    if decoder is None:
        decoder = _DecoderHelper(obj_type)
    _json_decoders.register(decoder, key=name)


def decode(json_data: Mapping, *, data_key: str = DEFAULT_DATA_KEY):
    key = json_data.get(DEFAULT_CLASS_ID_KEY, None)
    if key is None:
        return json_data
    try:
        return _json_decoders[key](json_data[data_key])
    except Exception as err:
        msg = f'could not deserialize JSON data {json_data!r}'
        raise JSONDeserializationValueError(msg) from err


dump = functools.partial(json.dump, default=encode)
dumps = functools.partial(json.dumps, default=encode)
load = functools.partial(json.load, object_hook=decode)
loads = functools.partial(json.loads, object_hook=decode)
