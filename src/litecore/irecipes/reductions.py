import itertools
import operator

from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
    Optional,
    Sequence,
    Tuple,
)

import litecore.irecipes.common as _common
from litecore.irecipes.typealiases import FilterFunc, KeyFunc


def ilen(iterable: Iterable[Any]) -> int:
    """Return the length of an iterable.

    Use this function when it is impractical or wasteful to pull an entire
    iterator into memory via list() in order to compute the length.

    If iterable is an iterator, will consume the entire iterator.

    Will not return if passed an infinite iterator.

    Arguments:
        iterable: object for which length is to be computed

    Returns:
        the number of items in the iterable

    Examples:

    >>> it = iter(range(10))
    >>> ilen(it)
    10
    >>> next(it)
    Traceback (most recent call last):
     ...
    StopIteration
    >>> ilen(range(10)) == len(range(10))
    True
    >>> ilen(c for c in 'slow way to get len') == len('slow way to get len')
    True
    >>> ilen('should be fast') == len('should be fast')
    True

    """
    try:
        return len(iterable)
    except TypeError:
        counter = itertools.count()
        _common.consume(zip(iterable, counter))
        return next(counter)


def iminmax(
        iterable: Iterable[Any],
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> Tuple[Any, Any]:
    """Return both the min and max items of an iterable.

    The algorithm used here only iterates through the items once. This function
    is meant to be used in cases where it is expensive to compute the
    relative item ordering (either in terms of the underlying objects or the
    key), and both the min and max items are required. Otherwise, just
    use the built-ins min() and max().

    The optional keyword argument key specifies a callable which will be used
    to determine the relative ordering of the items.

    If the iterable is an iterator, the entire iterator will be consumed.

    Will not return if passed an infinite iterator.

    Arguments:
        iterable: object for which min and max items are to be determined

    Keyword Arguments:
        key: single-argument callable which will be applied to each item and
            the result of which will be used to determine relative ordering
            of the items (optional; default is None, resulting in the use
            of each item unmodified)

    Returns:
        tuple of the min and max items of iterable

    Raises:
        ValueError: if an empty iterable is passed

    The examples shown here are purely for illustration and doctest. In
    practice, just use the built-ins min() and max() for these simple cases.

    A more practical example (outside the scope of this documentation) would
    be to iterate over a range of complex objects (e.g., simulation results,
    machine learning model fits, etc.) with a complex fitness criterion.

    Examples:

    >>> iminmax(range(8))
    (0, 7)
    >>> iminmax('the quick brown fox jumped'.split())
    ('brown', 'the')
    >>> iminmax('the quick brown fox jumped'.split(), key=len)
    ('the', 'jumped')
    >>> iminmax(['a'])
    ('a', 'a')
    >>> iminmax(())
    Traceback (most recent call last):
     ...
    ValueError: empty iterable

    """
    keyed = _common.keyed_items(iterable, key=key)
    try:
        lo_key, lo = next(keyed)
    except StopIteration:
        raise ValueError('empty iterable')
    hi_key, hi = lo_key, lo
    contiguous = itertools.zip_longest(keyed, keyed, fillvalue=(lo_key, lo))
    for (x_key, x), (y_key, y) in contiguous:
        if x_key > y_key:
            x_key, x, y_key, y = y_key, y, x_key, x
        if x_key < lo_key:
            lo_key, lo = x_key, x
        if y_key > hi_key:
            hi_key, hi = y_key, y
    return lo, hi


def count_where(
        iterable: Iterable[Any],
        predicate: FilterFunc = bool,
) -> int:
    """Count how many times the predicate is True for items of iterable.

    Same as quantify() from the standard library itertools recipes. See:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Arguments:
        iterable: object with items to be checked
        predicate: single-argument callable returning a boolean value

    Returns:
        number of times the predicate tests True for the items of the iterable

    Examples:

    >>> count_where(range(10), lambda n: n % 2 == 0)
    5
    >>> data = [1, 2, 3, 'a', 'b', 'c', len, str, int, 'd', 4]
    >>> count_where(data, lambda x: type(x) is str)
    4

    """
    return sum(map(predicate, iterable))


def allpairs(
        iterable: Iterable[Any],
        op: Callable[[Any, Any], bool],
) -> bool:
    """Returns True if all consecutive pairs of an iterable satify a condition.

    Arguments:
        iterable: object to be checked
        op: two-argument callable returning a boolean value

    Returns:
        True if every consecutive pair of items of the iterable satisfy the
        specified condition

    Examples:

    >>> allpairs(range(10), lambda x1, x2: x2 - x1 == 1)
    True

    """
    return all(
        op(left, right)
        for left, right in _common.pairwise(iterable)
    )


def decreasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is strictly decreasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is strictly decreasing, otherwise False

    Examples:

    >>> decreasing(range(10))
    False
    >>> decreasing('zyxw')
    True

    """
    return allpairs(iterable, operator.gt)


def increasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is strictly increasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is strictly increasing, otherwise False

    Examples:

    >>> increasing(range(10))
    True
    >>> increasing('zyxw')
    False

    """
    return allpairs(iterable, operator.lt)


def nondecreasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is non-decreasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is non-decreasing, otherwise False

    Examples:

    >>> nondecreasing(range(10))
    True
    >>> nondecreasing([0, 0, 1, 1, 2, 2, 3, 4])
    True
    >>> nondecreasing([0, 0, 1, 1, 2, 2, 5, 4])
    False

    """
    return allpairs(iterable, operator.le)


def nonincreasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is non-increasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is non-increasing, otherwise False

    Examples:

    >>> nonincreasing(reversed(range(10)))
    True
    >>> nonincreasing([5, 5, 4, 3, 2, 2, 1, 0])
    True
    >>> nonincreasing([5, 5, 4, 3, 2, 3, 1, 0])
    False

    """
    return allpairs(iterable, operator.ge)


def allequal(
        iterable: Iterable[Any],
        *,
        eq: Optional[Callable[[Any, Any], bool]] = None,
) -> bool:
    """Check whether all items of a general iterable are the same.

    The eq keyword argument, if provided, should specify a two-argument
    callable returning a boolean value representing equality. The default value
    of None corresponds to the usual equality operator.

    Returns True for an empty iterable. Will not return if passed an infinite
    iterator.

    See allequal_sequence() for a function specialized for built-in
    sequences such as lists and tuples.

    Arguments:
        iterable: object to be checked

    Keyword Arguments:
        eq: two-argument equality callable (optional; defaults to None)

    Returns:
        True if all items of iterable are the same (as defined by the equality
        keyword argument, if specified), otherwise False

    Examples:

    >>> allequal([1] * 5)
    True
    >>> allequal([])
    True
    >>> allequal(range(5))
    False
    >>> iterable = iter([0, 1, 1, 1])
    >>> next(iterable)
    0
    >>> allequal(iterable)
    True
    >>> allequal([2, 4, 6, 8], eq=lambda a, b: a % 2 == b % 2)
    True

    """
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return True
    if eq is None:
        return all(item == first for item in it)
    else:
        return all(eq(first, item) for item in it)


def allequal_sequence(sequence: Sequence[Any]) -> bool:
    """Check whether all items of a sequence are equal.

    This is an optimized form of allequal(), which should be faster for
    built-in sequences such as lists and tuples. Although it will work for any
    container implementing the interface of collections.abc.Sequence (see
    https://docs.python.org/3/library/collections.abc.html), the function
    allequal_sorted() should be faster on already-sorted general iterables.
    The general allequal() function may also be faster on
    user-defined iterable classes.

    Relies on the passed sequence having a count() method defined.

    Returns True for an empty sequence. Will not return if passed an infinite
    iterator.

    Arguments:
        sequence: object to be checked

    Returns:
        True if all items of sequence are the same, otherwise False

    Examples:

    >>> allequal_sequence([1] * 1000)
    True
    >>> allequal_sequence([1] * 999 + [2])
    False
    >>> allequal_sequence([set([3])] * 100)
    True
    >>> allequal_sequence([set([3])] * 99 + [set([4])])
    False
    >>> allequal_sequence([])
    True

    """
    try:
        return sequence.count(sequence[0]) == len(sequence)
    except IndexError:
        return True


def allequal_sorted(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> bool:
    """Check whether all items of a sorted iterable are the same.

    Note this function uses itertools.groupby(), which assumes the iterable
    is sorted by some key in order to work as expected. Whichever key function
    was used to sort the iterable should also be provided to this function
    via the optional key keyword argument. The key argument defaults to None,
    which is appropriate when the iterable was sorted wihtout using a custom
    key.

    See allequal_sequence() for a function specialized for built-in sequences
    such as lists and tuples.

    Returns True for an empty iterable. Will not return if passed an infinite
    iterator.

    Arguments:
        iterable: object to be checked

    Keyword Arguments:
        key: one-argument sort key callable (optional; defaults to None)

    Returns:
        True if all items of iterable are the same (as defined by the sort key,
        if specified), otherwise False

    Examples:

    >>> allequal_sorted([1] * 1000)
    True
    >>> allequal_sorted([1] * 999 + [2])
    False
    >>> allequal_sorted([set([3])] * 100)
    True
    >>> allequal_sorted([set([3])] * 99 + [set([4])])
    False
    >>> allequal_sorted([])
    True

    """
    groups = itertools.groupby(iterable, key)
    return next(groups, True) and not next(groups, False)


def allunique(iterable: Iterable[Any]) -> bool:
    """Check whether all items of an iterable are distinct.

    Works for either hashable or unhashable items. If all items are hashable,
    allunique_hashable() will be much faster.

    Returns True for an empty iterable. Will not return if passed an infinite
    iterator.

    Arguments:
        iterable: object to be checked

    Returns:
        True if all items of iterable are different, otherwise False

    Examples:

    >>> allunique(range(100))
    True
    >>> allunique(iter(range(100)))
    True
    >>> allunique(list(range(100)) + [9])
    False
    >>> allunique(['alice', 'bob', 'charlie'])
    True
    >>> allunique('hi ho')
    False
    >>> allunique([['this', 'object'], ['is'], ['not', 'hashable']])
    True
    >>> allunique([])
    True

    """
    seen = []
    saw = seen.append
    return not any(item in seen or saw(item) for item in iterable)


def allunique_hashable(iterable: Iterable[Hashable]) -> bool:
    """Check whether all items of an iterable are distinct.

    Only works for hashable items. If at least one item is unhashable,
    use allunique().

    Returns True for an empty iterable. Will not return if passed an infinite
    iterator.

    Arguments:
        iterable: object to be checked

    Returns:
        True if all items of iterable are different, otherwise False

    Examples:

    >>> allunique_hashable(range(100))
    True
    >>> allunique_hashable(iter(range(100)))
    True
    >>> allunique_hashable(list(range(100)) + [9])
    False
    >>> allunique_hashable(['alice', 'bob', 'charlie'])
    True
    >>> allunique_hashable('hi ho')
    False
    >>> allunique_hashable([['this', 'object'], ['is'], ['not', 'hashable']])
    Traceback (most recent call last):
     ...
    TypeError: unhashable type: 'list'
    >>> allunique_hashable([])
    True

    """
    seen = set()
    saw = seen.add
    return not any(item in seen or saw(item) for item in iterable)
