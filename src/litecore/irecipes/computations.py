from typing import (
    Any,
    Iterable,
    Iterator,
)

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
    return (x[1] - x[0] for x in _common.pairwise(iterable))


def proportional_changes(iterable: Iterable[Any]) -> Iterator[Any]:
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

    >>> [round(p, 3) for p in proportional_changes(range(1, 10))]
    [1.0, 0.5, 0.333, 0.25, 0.2, 0.167, 0.143, 0.125]
    >>> [round(p, 3) for p in proportional_changes([x * x for x in range(1, 10)])]
    [3.0, 1.25, 0.778, 0.562, 0.44, 0.361, 0.306, 0.266]

    """
    return ((x[1] - x[0]) / x[0] for x in _common.pairwise(iterable))
