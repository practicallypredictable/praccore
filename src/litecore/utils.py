import functools
import inspect
import logging
import types

from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

log = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf-8'


def isfunction(obj: Any) -> bool:
    if not callable(obj):
        return False
    return isinstance(obj, (
        types.BuiltinFunctionType,
        types.FunctionType,
        types.MethodType,
        types.LambdaType,
        functools.partial,
    ))


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


def get_caller_module():
    caller = inspect.stack()[2][0]
    return caller.f_globals['__name__']


def argslen(func):
    return len(getattr(inspect.signature(func), 'parameters'))
