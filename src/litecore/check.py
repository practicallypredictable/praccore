__all__ = (
    'is_iterable',
    'is_iterator',
)

import collections
import inspect

from typing import (
    Any,
    Tuple,
    Type,
)


def is_class(obj: Any) -> bool:
    return inspect.isclass(obj)


def is_iterable(
        obj: Any,
        *,
        only_registered: bool = False,
        excluded: Tuple[Type] = (str, bytes),
) -> bool:
    if excluded is not None and isinstance(obj, excluded):
        return False
    elif isinstance(obj, collections.abc.Iterable):
        return True
    elif not only_registered:
        try:
            iter(obj)
        except TypeError:
            return False
        else:
            return True
    else:
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
