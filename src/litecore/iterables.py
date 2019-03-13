import itertools
import functools
import operator

from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
    Optional,
    TypeVar,
)

from .sentinel import NO_VALUE

T = TypeVar('T')


def first(
        iterable: Iterable[Any],
        *,
        key: Optional[Callable[[Any], bool]] = None,
        default: Optional[Any] = None,
) -> Any:
    """Return first item of an iterable for which a condition is true.

    The default condition is to just return the first item in the iterable
    (i.e., the implicit condition is that the item exists).

    If the iterable is empty, or no value is found matching the desired
    condition, return the default value (None if unspecified).

    If the iterable is an iterator, its items up to and including the first to
    test True will be consumed.

    Arguments:
        iterable: object of which first item is to be returned

    Keyword Arguments:
        key: callable defining condition to be tested
            (optional, default is None)
        default: value to return if the passed iterable is empty or there is
            no item for which the condition is True
            (optional, defaults to None)

    Returns:
        First item of the passed iterable, or the default

    >>> data = [False, None, 0, '', (), 1, 2, 3, 4]
    >>> first(data)
    False
    >>> first(data[:5], key=bool) is None
    True
    >>> first(data, key=bool)
    1
    >>> first(data, key=lambda x: x % 2 == 0)
    2
    >>> first(data, key=lambda x: x > 4, default='missing')
    missing
    >>> first(data, key=lambda x: type(x) is int)
    0

    """
    if key is None:
        return next(iter(iterable), default)
    else:
        for item in iterable:
            if key(item):
                return item
        return default


def all_equal(one: Iterable[T], other: Iterable[T]) -> bool:
    try:
        if len(one) != len(other):
            return False
        return all(x == y for x, y in zip(one, other))
    except TypeError:
        for x, y in itertools.zip_longest(one, other, fillvalue=NO_VALUE):
            if NO_VALUE in (x, y) or x != y:
                return False
        return True


def hash_reduce(
        iterable: Iterable[Hashable],
        *,
        operation: Callable[[int, int], int] = operator.xor,
) -> int:
    hashes = map(hash, iterable)
    return functools.reduce(operation, hashes, 0)
