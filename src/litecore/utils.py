import logging

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Union,
)

import litecore.check

log = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf-8'


def to_str(
        str_or_bytes: Union[str, bytes],
        *,
        decode_from: str = DEFAULT_ENCODING,
) -> str:
    if isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(decode_from)
    else:
        return str_or_bytes


def to_bytes(
        str_or_bytes: Union[str, bytes],
        *,
        encode_to: str = DEFAULT_ENCODING,
) -> bytes:
    if isinstance(str_or_bytes, str):
        return str_or_bytes.encode(encode_to)
    else:
        return str_or_bytes

# TODO: bytesarray?


def to_dict(
        obj: Any,
        *,
        class_name_key: Optional[str] = None,
        skip_callables: bool = True,
        skip_private: bool = True,
) -> Dict[str, Any]:
    # TODO: FIX THIS?
    # https://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary/22679824#22679824

    def _skip_key(key: str) -> bool:
        if skip_private and key.startswith('_'):
            return True
        return False

    def _skip_item(item: Any) -> bool:
        if skip_callables and callable(item):
            return True
        return False

    def _process_dict(obj: Any, *, class_name_key: Optional[str] = None,):
        items = {
            key: to_dict(item, class_name_key=class_name_key)
            for key, item in obj.items()
            if not _skip_key(key) and not _skip_item(item)
        }
        if class_name_key is not None and hasattr(obj, '__class__'):
            items[class_name_key] = obj.__class__.__name__
        return items

    if litecore.check.is_str_or_bytes(obj):
        return obj
    elif litecore.check.is_mapping(obj):
        return _process_dict(obj)
    elif litecore.check.is_iterable(obj):
        return [to_dict(item, class_name_key=class_name_key) for item in obj]
    elif hasattr(obj, '_ast'):
        return to_dict(obj._ast())
    elif hasattr(obj, '_asdict'):
        return to_dict(obj._asdict())
    elif hasattr(obj, '__dict__'):
        return _process_dict(vars(obj), class_name_key=class_name_key)
    elif hasattr(obj, '__slots__'):
        slots = dict((slot, getattr(obj, slot)) for slot in obj.__slots__)
        return to_dict(slots, class_name_key=class_name_key)
    else:
        return obj


class _ConstantFunction:
    def __init__(self, value):
        self._value = value

    def __call__(self):
        return self._value


def constant_factory(constant: Any) -> Callable[[], Any]:
    return _ConstantFunction(constant)


_BUILTINS = str.__class__.__module__


def full_class_name(obj):
    cls = type(obj)
    module = cls.__module__
    if module is None or module == _BUILTINS:
        return cls.__qualname__
    else:
        return f'{module}.{obj.__class__.__qualname__}'


def bind(func, instance, *, name: Optional[str] = None):
    if name is None:
        name = func.__name__
    bound_method = func.__get__(instance)
    setattr(instance, name, bound_method)
    return bound_method


def args_kwargs_repr(*args, **kwargs) -> str:
    args_repr = [repr(arg) for arg in args]
    kwargs_repr = [f'{key}={value}' for key, value in kwargs.items()]
    return ', '.join(args_repr + kwargs_repr)
