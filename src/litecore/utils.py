import collections
import functools
import inspect
import itertools
import types

from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Union,
)


DEFAULT_ENCODING = 'utf-8'
BULITIN_MODULE = str.__class__.__module__


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


def constant_factory(constant: Any) -> Callable[[], Any]:
    return itertools.repeat(constant).__next__


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


def raises(exc: Exception, func: Callable) -> bool:
    try:
        func()
        return False
    except exc:
        return True


class classproperty:
    def __init__(self, func: Callable):
        self._func = func

    def __get__(self, instance, cls):
        return self._func(cls)


def subclasses(cls):
    try:
        queue = collections.deque(cls.__subclasses__())
    except (AttributeError, TypeError) as err:
        msg = f'expected type object, got {cls!r}'
        raise TypeError(msg) from err
    seen = set()
    classes = []
    while queue:
        cls = queue.popleft()
        if cls in seen:
            continue
        seen.add(cls)
        classes.append(cls)
        queue.extend(cls.__subclasses__())
    return classes


def instancemethod(instance):
    def decorator(func):
        method = types.MethodType(func, instance, type(instance))
        setattr(instance, method.func_name, method)
        return method
    return decorator


def suppress(
        _func=None,
        *,
        exceptions: Optional[Iterable[Exception]] = None,
):
    if exceptions is None:
        exceptions = Exception
    else:
        exceptions = tuple(exceptions)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                pass
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def noexceptions(_func=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return True, func(*args, **kwargs)
            except Exception as err:
                False, err
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)
