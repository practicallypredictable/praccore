import collections
import inspect
import logging

from typing import (
    Any,
    Optional,
    Sequence,
    Type,
)

log = logging.getLogger(__name__)


def is_class(obj: Any) -> bool:
    return inspect.isclass(obj)


def is_iterable(
        obj: Any,
        *,
        ignore_types: Optional[Sequence[Type]] = None,
) -> bool:
    """Check whether an object is iterable.

    Checks whether the object can be passed to the built-in iter() function.
    Certain types can be forced to return False using the ignore_types keyword
    argument. This is useful for excluding types such as str, bytes and
    bytearray, which are natively iterable but which are often treated as
    non-iterable. (See, e.g., the flatten_recursive() function in the
    litecore.sequences sub-package).

    Arguments:
        obj: object to be checked

    Keyword Arguments:
        ignore_types: sequence of types for which checking is to return False
            (optional; defaults to None)

    Returns:
        True if the object can be passed to iter(), otherwise False.

    Examples:

    >>> is_iterable('abc')
    True
    >>> is_iterable('abc', ignore_types=(str, bytes, bytearray))
    False
    >>> is_iterable(range(10))
    True
    >>> is_iterable(2)
    False

    """
    if ignore_types is not None and isinstance(obj, ignore_types):
        return False
    elif isinstance(obj, collections.abc.Iterable):
        return True
    else:
        try:
            iter(obj)
            return True
        except TypeError:
            return False
    return False


def is_iterator(
        obj: Any,
        *,
        only_registered: bool = False,
) -> bool:
    if isinstance(obj, collections.abc.Iterator):
        return True
    elif not only_registered:
        try:
            # Iterator protocol is that iter(obj) returns obj, if obj is an
            #   iterator; for a container, the below expression is False
            return iter(obj) is iter(obj)
        except TypeError:
            return False
    else:
        return False
