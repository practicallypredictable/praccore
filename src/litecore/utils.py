import collections
import contextlib
import logging
import pathlib
import os

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Union,
)

import litecore.check

log = logging.getLogger(__name__)


class LitecoreError(Exception):
    """Base class for all exceptions raised by this package."""
    pass


_DEFAULT_ENCODING = 'utf-8'

DO_NOT_RECURSE = (str, bytes, bytearray)


def to_str(
        str_or_bytes: Union[str, bytes],
        *,
        decode_from: str = _DEFAULT_ENCODING,
) -> str:
    if isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(decode_from)
    else:
        return str_or_bytes


def to_bytes(
        str_or_bytes: Union[str, bytes],
        *,
        encode_to: str = _DEFAULT_ENCODING,
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

    if isinstance(obj, DO_NOT_RECURSE):
        return obj
    elif isinstance(obj, collections.abc.Mapping):
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


def constant_factory(constant: Any) -> Callable[[], Any]:
    return lambda: constant


def get_qualname(class_obj):
    module = class_obj.__module__
    try:
        class_name = class_obj.__qualname__
    except Exception:
        class_name = class_obj.__name__
        msg = (
            'Could not find qualname for %s in module %s; '
            'logging using name instead'
        )
        log.warning(msg, class_name, module)
    return class_name


def bind(func, instance, *, name: Optional[str] = None):
    if name is None:
        name = func.__name__
    bound_method = func.__get__(instance)
    setattr(instance, name, bound_method)
    return bound_method


def generic_repr(args, kwargs) -> str:
    positional = ', '.join(repr(arg) for arg in args)
    keyword = ', '.join(
        f'{key!r}={value!r}'
        for key, value in kwargs.items()
    )
    s = positional if positional else ''
    if positional and keyword:
        s += ', '
    if keyword:
        s += keyword
    return s


@contextlib.contextmanager
def cwd(path: pathlib.Path):
    """Change working directory and return to previous directory on exit."""
    current = pathlib.Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(current)
