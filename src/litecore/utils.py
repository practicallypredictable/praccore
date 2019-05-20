import collections
import dataclasses
import functools
import inspect
import itertools
import logging
import types

from typing import (
    Any,
    Callable,
    Optional,
    Sequence,
    Type,
    Union,
)

log = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf-8'
BULITIN_MODULE = str.__class__.__module__


def is_chars(obj: Any) -> bool:
    """

    Examples:

    >>> is_chars('a')
    True
    >>> is_chars(b'011')
    True
    >>> is_chars(2)
    False

    """
    return isinstance(obj, (str, bytes, bytearray))


def is_iterable(
        obj: Any,
        *,
        suppress_chars: bool = True,
        suppress_types: Optional[Sequence[Type]] = None,
) -> bool:
    """Check whether an object is iterable.

    Checks whether the object is iterable; i.e., it can be passed to the
    built-in iter() function.

    By default, characters (str, bytes, or bytearray) are treated as
    NON-iterable, even though these built-in types are iterable. This choice
    was made because in most situations when you'd want to check for an
    iterable, you would typically prefer to keep the str or bytes together
    as a discrete data unit. This can be overridden via the optional
    suppress_chars flag.

    Other types can also be forced to return False using the suppress_types
    keyword argument. Similar to the suppress_chars flag, this should be useful
    for situations where iterable types such as tuples and namedtuples are used
    as records and should be treated as discrete data units rather than
    iterated over.

    Arguments:
        obj: object to be checked

    Keyword Arguments:
        suppress_chars: boolean flag indicating whether to treat str or bytes
            as iterable (optional; defaults to True)
        suppress_types: sequence of types for which checking is to return False
            (optional; defaults to None)

    Returns:
        True if the object is an iterable, otherwise False.

    Examples:

    >>> is_iterable(2)
    False
    >>> is_iterable('abc')
    False
    >>> is_iterable('abc', suppress_chars=False)
    True
    >>> is_iterable(tuple(range(10)))
    True
    >>> is_iterable(tuple(range(10)), suppress_types=(tuple,))
    False

    """
    if suppress_chars and isinstance(obj, (str, bytes, bytearray)):
        return False
    elif suppress_types is not None and isinstance(obj, tuple(suppress_types)):
        return False
    elif isinstance(obj, collections.abc.Iterable):
        return True
    else:
        try:
            iter(obj)
            return True
        except TypeError:
            return False


def is_iterator(obj: Any) -> bool:
    """Check whether an object is an iterator.

    Checks whether the object follows the iterator protocol: iter(obj) is obj
    if obj is an iterator.

    Arguments:
        obj: object to be checked

    Returns:
        True if the object is an iterator, otherwise False.

    Examples:

    >>> is_iterator(range(10))
    False
    >>> is_iterator(iter(range(10)))
    True

    """
    if isinstance(obj, collections.abc.Iterator):
        return True
    else:
        try:
            return iter(obj) is iter(obj)
        except TypeError:
            return False


def is_namedtuple_instance(obj: Any) -> bool:
    cls = type(obj)
    bases = cls.__bases__
    if len(bases) != 1 or bases[0] is not tuple:
        return False
    fields = getattr(cls, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(field) is str for field in fields)


def is_dataclass_instance(obj: Any) -> bool:
    return dataclasses.is_dataclass(obj) and not isinstance(obj, type)


def is_function(obj: Any) -> bool:
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
