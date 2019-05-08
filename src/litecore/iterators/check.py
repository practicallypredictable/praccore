import collections

from typing import (
    Any,
    Optional,
    Sequence,
    Type,
)


def isiterable(
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

    >>> isiterable(2)
    False
    >>> isiterable('abc')
    False
    >>> isiterable('abc', suppress_chars=False)
    True
    >>> isiterable(tuple(range(10)))
    True
    >>> isiterable(tuple(range(10)), suppress_types=(tuple,))
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


def isiterator(obj: Any) -> bool:
    """Check whether an object is an iterator.

    Checks whether the object follows the iterator protocol: iter(obj) is obj
    if obj is an iterator.

    Arguments:
        obj: object to be checked

    Returns:
        True if the object is an iterator, otherwise False.

    Examples:

    >>> isiterator(range(10))
    False
    >>> isiterator(iter(range(10)))
    True

    """
    if isinstance(obj, collections.abc.Iterator):
        return True
    else:
        try:
            return iter(obj) is iter(obj)
        except TypeError:
            return False
