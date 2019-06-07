
import collections
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

from litecore.sentinels import NO_VALUE as _NO_VALUE
import litecore.irecipes.common as _common
from litecore.irecipes.typealiases import FilterFunc


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


def count_true(
        iterable: Iterable[Any],
        predicate: FilterFunc = bool,
) -> int:
    """

    Examples:

    >>> count_true(range(10), lambda n: n % 2 == 0)
    5
    >>> data = [1, 2, 3, 'a', 'b', 'c', len, str, int, 'd', 4]
    >>> count_true(data, lambda x: type(x) is str)
    4

    """
    return sum(map(predicate, iterable))


def _consecutive_pairs(iterable: Iterable[Any], op: Callable) -> bool:
    # Helper function for the sequence comparisons below
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
        True if the iterable is strictly decreasing, otherwise False.

    Examples:

    >>> decreasing(range(10))
    False
    >>> decreasing('zyxw')
    True

    """
    return _consecutive_pairs(iterable, operator.gt)


def increasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is strictly increasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is strictly increasing, otherwise False.

    Examples:

    >>> increasing(range(10))
    True
    >>> increasing('zyxw')
    False

    """
    return _consecutive_pairs(iterable, operator.lt)


def non_decreasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is non-decreasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is non-decreasing, otherwise False.

    Examples:

    >>> non_decreasing(range(10))
    True
    >>> non_decreasing([0, 0, 1, 1, 2, 2, 3, 4])
    True
    >>> non_decreasing([0, 0, 1, 1, 2, 2, 5, 4])
    False

    """
    return _consecutive_pairs(iterable, operator.le)


def non_increasing(iterable: Iterable[Any]) -> bool:
    """Returns True if the iterable is non-increasing.

    Every item of the iterable must have rich comparisons defined between them.

    Arguments:
        iterable: object to be checked

    Returns:
        True if the iterable is non-increasing, otherwise False.

    Examples:

    >>> non_increasing(reversed(range(10)))
    True
    >>> non_increasing([5, 5, 4, 3, 2, 2, 1, 0])
    True
    >>> non_increasing([5, 5, 4, 3, 2, 3, 1, 0])
    False

    """
    return _consecutive_pairs(iterable, operator.ge)


def all_equal_items(
        iterable: Iterable[Any],
        *,
        eq: Optional[Callable[[Any, Any], bool]] = None,
) -> bool:
    """Check whether all items of a general iterable are the same.

    The eq keyword argument, if provided, should specify a two-argument
    callable returning a boolean value representing equality. The default value
    of None correponds to the usual equality operator.

    Arguments:
        iterable: object to be checked

    Keyword Arguments:
        eq: two-argument equality callable (optional; defaults to None)

    Returns:
        True if all items of iterable are the same (as defined by the equality
        keyword argument, if specified), otherwise False.

    Note:
        * Returns True for an empty iterable.
        * See all_equal_items_sequence() for a function specialized for
          built-in sequences such as lists and tuples.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> all_equal_items([1] * 5)
    True
    >>> all_equal_items([])
    True
    >>> all_equal_items(range(5))
    False
    >>> iterable = iter([0, 1, 1, 1])
    >>> next(iterable)
    0
    >>> all_equal_items(iterable)
    True
    >>> all_equal_items([2, 4, 6, 8], eq=lambda a, b: a % 2 == b % 2)
    True

    """
    it = iter(iterable)
    if eq is None:
        eq = operator.eq
    try:
        first = next(it)
    except StopIteration:
        return True
    return all(eq(first, item) for item in it)


def all_equal_items_sequence(sequence: Sequence[Any]) -> bool:
    """Check whether all items of a sequence are equal.

    This is an optimized form of all_equal_items() below, which should be
    faster for built-in sequences such as lists. Although it will work for any
    container implementing the interface of collections.abc.Sequence (see
    https://docs.python.org/3/library/collections.abc.html), the function
    all_equal_items_sorted() function should be faster on already-sorted
    iterables. The general all_equal_items() function may also be faster on
    user-defined iterable classes.

    Arguments:
        sequence: object to be checked

    Returns:
        True if all items of sequence are the same, otherwise False.

    Note:
        * Returns True for an empty sequence.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> all_equal_items_sequence([1] * 1000)
    True
    >>> all_equal_items_sequence([1] * 999 + [2])
    False
    >>> all_equal_items_sequence([set([3])] * 100)
    True
    >>> all_equal_items_sequence([set([3])] * 99 + [set([4])])
    False
    >>> all_equal_items_sequence([])
    True

    """
    try:
        return sequence.count(sequence[0]) == len(sequence)
    except IndexError:
        return True


def all_equal_items_sorted(
        iterable: Iterable[Any],
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> bool:
    """Check whether all items of a sorted iterable are the same.

    Note this function uses itertools.groupby, which assumes the iterable
    is sorted by some key in order to work as expected. Whichever key function
    was used to sort the iterable should also be provided to this function
    via the optional key keyword argument. The key argument defaults to None,
    which is appropriate when the iterable was sorted wihtout using a custom
    key.

    Arguments:
        iterable: object to be checked

    Keyword Arguments:
        key: one-argument sort key callable (optional; defaults to None)

    Returns:
        True if all items of iterable are the same (as defined by the sort key,
        if specified), otherwise False.

    Note:
        * Returns True for an empty iterable.
        * See all_equal_items_sequence() for a function specialized for
          built-in sequences such as lists and tuples.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> all_equal_items_sorted([1] * 1000)
    True
    >>> all_equal_items_sorted([1] * 999 + [2])
    False
    >>> all_equal_items_sorted([set([3])] * 100)
    True
    >>> all_equal_items_sorted([set([3])] * 99 + [set([4])])
    False
    >>> all_equal_items_sorted([])
    True

    """
    groups = itertools.groupby(iterable, key)
    return next(groups, True) and not next(groups, False)


def all_distinct_items(iterable: Iterable[Any]) -> bool:
    """Check whether all items of an iterable are distinct.

    Arguments:
        iterable: object to be checked

    Returns:
        True if all items of iterable are different, otherwise False.

    Note:
        * Returns True for an empty iterable.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> all_distinct_items(range(1_000_000))
    True
    >>> all_distinct_items(iter(range(10_000)))
    True
    >>> all_distinct_items(list(range(10_000)) + [9])
    False
    >>> all_distinct_items(['alice', 'bob', 'charlie'])
    True
    >>> all_distinct_items('hi ho')
    False
    >>> all_distinct_items([])
    True

    """
    n = None
    try:
        n = len(iterable)
    except TypeError:
        pass
    if n is not None and n < 100_000:  # TODO: optimize this
        return n == len(set(iterable))
    else:
        hashables_seen = set()
        saw_hashable = hashables_seen.add  # optimization
        unhashables_seen = []
        saw_unhashable = unhashables_seen.append  # optimization
        for item in iterable:
            try:
                if item in hashables_seen:
                    return False
                else:
                    saw_hashable(item)
            except TypeError:
                if item in unhashables_seen:
                    return False
                else:
                    saw_unhashable(item)
        return True


def same_items_unhashable(*iterables: Tuple[Iterable[Any]]) -> bool:
    """Check whether passed iterables contain the same (unordered) items.

    The iterables can be of different types, only the underlying items are
    compared for equality. The underlying items do not need to be hashable.

    However, the algorithm reuqired for general unhashable items is quite slow.
    For situations where the items are known to be hashable, use same_items().

    The order of the items in each underlying iterable (if applicable), is
    ignored. For ordered comparison, see the function same_ordered_items().

    Arguments:
        tuple of iterables: objects to be compared; must have at least 2 items

    Returns:
        Boolean whether the iterables all contain same items, irrespective of
        the order of their items.

    Raises:
        ValueError: if less than 2 iterables are passed as positional arguments

    Note:
        * Any iterators passed as arguments will be consumed.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> items = [(i, i+1) for i in range(10)]
    >>> import random
    >>> shuffled = items[:]
    >>> random.shuffle(shuffled)
    >>> different = items[:-1] + [None]
    >>> longer = items + [None]
    >>> set_items = [set(item) for item in items]
    >>> shuffled_set_items = set_items.copy()
    >>> items_it = iter(set_items)
    >>> shuffled_items_it = iter(shuffled_set_items)
    >>> random.shuffle(shuffled_set_items)
    >>> same_items_unhashable(items, set(items))
    True
    >>> same_items_unhashable(items_it, shuffled_items_it)
    True
    >>> same_items_unhashable(items, reversed(items))
    True
    >>> same_items_unhashable(items, reversed(items), shuffled)
    True
    >>> same_items_unhashable(items, shuffled, different)
    False
    >>> same_items_unhashable(items, shuffled, longer)
    False
    >>> same_items_unhashable(set_items, set_items)
    True
    >>> same_items_unhashable(set_items, shuffled_set_items)
    True

    """
    if len(iterables) < 2:
        msg = f'Got {len(iterables)} iterables; must provide at least 2'
        raise ValueError(msg)
    reference = list(iterables[0])
    for test in iterables[1:]:
        unmatched = reference[:]
        for item in test:
            try:
                unmatched.remove(item)
            except ValueError:
                return False
        if unmatched:
            return False
    return True


def same_items(*iterables: Tuple[Iterable[Hashable]]) -> bool:
    """Check whether passed iterables contain the same (unordered) items.

    The iterables can be of different types, only the underlying items are
    compared for equality. The underlying items must be hashable.

    The order of the items in each underlying iterable (if applicable), is
    ignored. For ordered comparison, see the function same_ordered_items().

    To perform a similar computer on unhashable items, see the function
    same_items_unhashable().

    Arguments:
        tuple of iterables: objects to be compared; must have at least 2 items

    Returns:
        Boolean whether the iterables all contain same items, irrespective of
        the order of their items.

    Raises:
        ValueError: if less than 2 iterables are passed as positional arguments

    Note:
        * Any iterators passed as arguments will be consumed.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> items = [(i, i+1) for i in range(10)]
    >>> import random
    >>> shuffled = items[:]
    >>> random.shuffle(shuffled)
    >>> different = items[:-1] + [None]
    >>> longer = items + [None]
    >>> set_items = [set(item) for item in items]
    >>> same_items(items, set(items))
    True
    >>> same_items(items, reversed(items))
    True
    >>> same_items(items, reversed(items), shuffled)
    True
    >>> same_items(items, shuffled, different)
    False
    >>> same_items(items, shuffled, longer)
    False
    >>> same_items(set_items, set_items)
    Traceback (most recent call last):
     ...
    TypeError: unhashable type: 'set'

    """
    if len(iterables) < 2:
        msg = f'Got {len(iterables)} iterables; must provide at least 2'
        raise ValueError(msg)
    first = collections.Counter(iterables[0])
    return all(collections.Counter(it) == first for it in iterables[1:])


def same_ordered_items(*iterables: Tuple[Iterable[Any]]) -> bool:
    """Check whether passed iterables contain the same items in same order.

    The iterables can be of different types, only the underlying items are
    compared for equality. The underlying items do not have to be hashable.

    The order of the items in each underlying iterable must match to return
    True. For unordered comparison, see the function same_items().

    Arguments:
        tuple of iterables: objects to be compared; must have at least 2 items

    Returns:
        Boolean whether the iterables all contain same items, irrespective of
        the order of their items.

    Raises:
        ValueError: if less than 2 iterables are passed as positional arguments

    Note:
        * Any iterators passed as arguments will be consumed.
        * Will not return if passed an infinite iterator.

    Examples:

    >>> items = [(i, i+1) for i in range(10)]
    >>> import random
    >>> shuffled = items[:]
    >>> random.shuffle(shuffled)
    >>> different = items[:-1] + [None]
    >>> assert len(items) == len(different)
    >>> longer = items + [None]
    >>> assert len(items) < len(longer)
    >>> set_items = [set(item) for item in items]
    >>> shuffled_set_items = set_items.copy()
    >>> random.shuffle(shuffled_set_items)
    >>> same_ordered_items(items, items, items)
    True
    >>> same_ordered_items(items, reversed(items))
    False
    >>> same_ordered_items(items, reversed(items), shuffled)
    False
    >>> same_ordered_items(items, shuffled, different)
    False
    >>> same_ordered_items(items, shuffled, longer)
    False
    >>> same_ordered_items(set_items, set_items)
    True
    >>> same_ordered_items(set_items, shuffled_set_items)
    False

    """
    if len(iterables) < 2:
        msg = f'Got {len(iterables)} iterables; must provide at least 2'
        raise ValueError(msg)
    zipped_items = itertools.zip_longest(*iterables, fillvalue=_NO_VALUE)
    return all(all_equal_items_sequence(item) for item in zipped_items)


def inner_product(
    left: Iterable[Any],
    right: Iterable[Any],
    *,
    operation: Callable[[Any, Any], Any] = operator.mul,
    mapping: Callable = map,
    reduction: Callable[[Iterable[Any]], Any] = sum,
) -> Any:
    """

    >>> inner_product(range(1, 5), range(1, 5)) == 1 + 4 + 9 + 16
    True
    >>> c1 = [complex(1, -1), complex(3, 5)]
    >>> c2 = [complex(2, 2), complex(-3, 1)]
    >>> inner_product(c1, c2)
    (-10-12j)
    >>> animals = ['alpaca', 'cat', 'dog', 'frog', 'zebra']
    >>> foods = ['avocado', 'banana', 'doughnuts', 'fries', 'goulash']
    >>> def start_same(s1, s2): return s1.lower()[0] == s2.lower()[0]
    >>> inner_product(animals, foods, operation=start_same)
    3

    """
    return reduction(mapping(operation, left, right))
