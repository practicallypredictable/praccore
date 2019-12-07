import collections.abc
import dataclasses
import functools
import inspect
import itertools
import types

from typing import (
    Any,
    Callable,
    Hashable,
    Iterator,
    Optional,
    Tuple,
    Type,
    Union,
)


def are_all(obj_type, *args) -> bool:
    return all(isinstance(arg, obj_type) for arg in args)


def is_chars(obj: Any) -> bool:
    """Check if an object is one of the built-in character types.

    The built-in data types representing characters in Python 3 are:
        str, bytes, bytearray

    Arguments:
        obj: object to be checked

    Returns:
        True if the object is an instance of str, bytes or bytearray,
        otherwise False

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
        exclude_types: Optional[Tuple[Type, ...]] = None,
) -> bool:
    """Check if an object is iterable.

    By default, characters (str, bytes, or bytearray) are treated as
    NOT being iterable, even though these built-in types are normally
    iterable. In most situations where it would make sense to check for
    an iterable (e.g., recursion through a nested data structure), it
    would typically make sense to not treat characters as iterable.

    This behavior can be modified by the keyword arguments. Other types
    can also be forced to return False. This should be useful
    for situations where iterable types such as tuples and namedtuples
    are used as records and should be treated as discrete data units
    rather than iterated over.

    Arguments:
        obj: object to be checked

    Keyword Arguments:
        suppress_chars: boolean flag indicating whether to treat str,
            bytes and bytearrays as iterable (defaults to True)
        exclude: iterable of types for which checking is to
            return False (optional; defaults to None)

    Returns:
        True if the object is an iterable, otherwise False

    Examples:

    >>> is_iterable(2)
    False
    >>> is_iterable('abc')
    False
    >>> is_iterable('abc', suppress_chars=False)
    True
    >>> is_iterable(tuple(range(10)))
    True
    >>> is_iterable(tuple(range(10)), exclude_types=(tuple,))
    False

    """
    if suppress_chars and is_chars(obj):
        return False
    elif exclude_types is not None and isinstance(obj, exclude_types):
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

    Checks whether the object follows the iterator protocol:
        iter(obj) is obj == True, if obj is an iterator.

    Arguments:
        obj: object to be checked

    Returns:
        True if the object is an iterator, otherwise False

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
            return iter(obj) is obj
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


def iter_attrs(obj: Any) -> Iterator[Tuple[str, Any]]:
    try:
        slots_iter = (
            (slot, getattr(obj, slot))
            for slot in getattr(obj, '__slots__')
        )
    except AttributeError:
        slots_iter = iter(())
    return itertools.chain(vars(obj).items(), slots_iter)


def filter_attributes(
        attr: Tuple[str, Any],
        *,
        keep_callable: bool = False,
        keep_sunder: bool = False,
        keep_dunder: bool = False,
) -> bool:
    key, value = attr
    if callable(value):
        return keep_callable
    if key.startswith('__'):
        return keep_dunder
    if key.startswith('_'):
        return keep_sunder
    return True


ObjectGetterReturnType = Union[None, Iterator[Tuple[Union[int, Hashable], Any]]]
ChildObjectGetter = Callable[[Any], ObjectGetterReturnType]


def child_objects(
        obj: Any,
        *,
        exclude_types: Optional[Tuple[Type, ...]] = None,
        class_attr_filter: Optional[Callable[..., bool]] = filter_attributes,
) -> ObjectGetterReturnType:
    if exclude_types is not None and isinstance(obj, exclude_types):
        return
    elif is_chars(obj):
        return
    elif is_dataclass_instance(obj):
        iterator = dataclasses.asdict(obj).items()
    elif is_namedtuple_instance(obj):
        iterator = obj._asdict().items()
    elif isinstance(obj, collections.abc.Mapping):
        return obj.items()
    elif is_iterable(obj):
        return enumerate(obj)
    elif inspect.isclass(obj):
        iterator = iter_attrs(obj)
    else:
        return
    if class_attr_filter is not None:
        return filter(class_attr_filter, iterator)
    else:
        return iterator
