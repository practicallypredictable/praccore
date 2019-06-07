from typing import (
    Any,
    Iterable,
    Iterator,
    Optional,
)

from litecore.sentinels import NO_VALUE as _NO_VALUE
import litecore.irecipes.common as _common


def difference(iterable: Iterable[Any]) -> Iterator[Any]:
    """Take first differences of items of an iterable.

    Assumes the subtraction operator makes sense for each item of the iterable.

    Arguments:
        iterable: object the items of which are to be differenced

    Returns:
        iterator of the first differences

    >>> list(difference(range(10)))
    [1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> list(difference([x * x for x in range(10)]))
    [1, 3, 5, 7, 9, 11, 13, 15, 17]
    >>> list(difference(difference([x * x for x in range(10)])))
    [2, 2, 2, 2, 2, 2, 2, 2]

    """
    return (x2 - x1 for x1, x2 in _common.pairwise(iterable))


def proportional_change(
        iterable: Iterable[Any],
        *,
        zero_divide_value: Optional[Any] = _NO_VALUE,
) -> Iterator[Any]:
    """Return proportional changes of the items of an iterable.

    Assumes the subtraction and division operators makes sense for each item of
    the iterable. A ZeroDivisionError will be raised if any of the items of the
    original iterable are zero.

    To get percent changes, just multiply the items from this function by 100.

    To get log changes, take the desired logarithm.

    Arguments:
        iterable: object the items of which are to be differenced

    Returns:
        iterator of the proportional changes

    >>> [round(p, 3) for p in proportional_change(range(1, 10))]
    [1.0, 0.5, 0.333, 0.25, 0.2, 0.167, 0.143, 0.125]
    >>> [round(p, 3) for p in proportional_change(range(0, 10))]
    Traceback (most recent call last):
     ...
    ZeroDivisionError: division by zero
    >>> [round(p, 3) for p in proportional_change(range(0, 10), zero_divide_value=float('NaN'))]
    [nan, 1.0, 0.5, 0.333, 0.25, 0.2, 0.167, 0.143, 0.125]

    """
    for x1, x2 in _common.pairwise(iterable):
        try:
            yield (x2 - x1) / x1
        except ZeroDivisionError:
            if zero_divide_value is not _NO_VALUE:
                yield zero_divide_value
            else:
                raise
