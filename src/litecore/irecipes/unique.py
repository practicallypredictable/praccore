"""Functions for testing or extracting unique values from iterables.

"""
import itertools

from typing import (
    Any,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
)

from litecore.irecipes.typealiases import (
    KeyFunc,
)


def unique_hashable(
        iterable: Iterable[Hashable],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Hashable]:
    """Return iterator of unique items from an iterable.

    The items in the iterable must be hashable.

    Same as standard library itertools recipes unique_everseen. See:
        https://docs.python.org/3/library/itertools.html

    The optional key is a single-argument callable that, if provided,
    will be called to produce a modified value for each item prior to
    determining uniqueness. Only items with different keys will compare
    as different. The default is None, which means that each item is
    tested for uniqueness without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None, signifying each item is
            to be processed without modification)

    Yields:
        2-tuples of unique values in the order they were encountered and
        the index of each item in the passed iterable

    >>> list(unique('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D']
    >>> list(unique('ABbcCAD', key=str.lower))
    ['A', 'B', 'c', 'D']
    >>> list(unique([]))
    []
    >>> sign = lambda x: -1 if x < 0 else 1
    >>> even = lambda x: x % 2 == 0
    >>> data = [-x if even(x) else x for x in range(1, 10)]
    >>> list(unique(data, key=sign))
    [1, -2]

    """
    seen = set()
    saw = seen.add
    already_seen = seen.__contains__
    if key is None:
        for item in itertools.filterfalse(already_seen, iterable):
            saw(item)
            yield item
    else:
        for item in iterable:
            item_key = key(item)
            if item_key not in seen:
                saw(item_key)
                yield item


def enumerate_unique(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Tuple[int, Any]]:
    """Return iterator of unique items with indices from an iterable.

    Similar to built-in enumerate(), except only the items with unique
    values will be included.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided,
    will be called to produce a modified value for each item prior to
    determining uniqueness. Only items with different keys will compare
    as different. The default is None, which means that each item is
    tested for uniqueness without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None, signifying each item is to be
            processed without modification)

    Yields:
        2-tuples of unique values in the order they were encountered and
        the index of each item in the passed iterable

    >>> list(enumerate_unique('AAAABBBCCDAABBB'))
    [(0, 'A'), (4, 'B'), (7, 'C'), (9, 'D')]
    >>> list(enumerate_unique('ABbcCAD', key=str.lower))
    [(0, 'A'), (1, 'B'), (3, 'c'), (6, 'D')]
    >>> list(enumerate_unique([]))
    []
    >>> list(enumerate_unique(range(10), key=type))
    [(0, 0)]
    >>> unhashable = [{'value': n, 'even': n % 2 == 0} for n in range(1, 10)]
    >>> import operator
    >>> list(enumerate_unique(unhashable, key=operator.itemgetter('even')))
    [(0, {'value': 1, 'even': False}), (1, {'value': 2, 'even': True})]

    """
    hashables_seen = set()
    saw_hashable = hashables_seen.add
    unhashables_seen = []
    saw_unhashable = unhashables_seen.append
    if key is None:
        for index, item in enumerate(iterable):
            try:
                if item not in hashables_seen:
                    saw_hashable(item)
                    yield index, item
            except TypeError:
                if item not in unhashables_seen:
                    saw_unhashable(item)
                    yield index, item
    else:
        for index, item in enumerate(iterable):
            item_key = key(item)
            try:
                if item_key not in hashables_seen:
                    saw_hashable(item_key)
                    yield index, item
            except TypeError:
                if item_key not in unhashables_seen:
                    saw_unhashable(item_key)
                    yield index, item


def unique(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Any]:
    """Return iterator of unique items from an iterable.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided,
    will be called to produce a modified value for each item prior to
    determining uniqueness. Only items with different keys will compare
    as different. The default is None, which means that each item is
    tested for uniqueness without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None, signifying each item is to be
            processed without modification)

    Yields:
        each unique value in the iterable in the order it is occurs in
        the passed iterable

    Examples:

    >>> list(unique('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D']
    >>> list(unique('ABbcCAD', key=str.lower))
    ['A', 'B', 'c', 'D']
    >>> list(unique([]))
    []
    >>> list(unique(range(10), key=type))
    [0]
    >>> unhashable = [{'value': n, 'even': n % 2 == 0} for n in range(1, 10)]
    >>> import operator
    >>> list(unique(unhashable, key=operator.itemgetter('even')))
    [{'value': 1, 'even': False}, {'value': 2, 'even': True}]

    """
    return (item for _, item in enumerate_unique(iterable, key=key))


def argunique(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[int]:
    """Return iterator of indices of unique items from an iterable.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided,
    will be called to produce a modified value for each item prior to
    determining uniqueness. Only items with different keys will compare
    as different. The default is None, which means that each item is
    tested for uniqueness without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None, signifying each item is to be
            processed without modification)

    Yields:
        indices of each unique value in the iterable in the order it is
        occurs in the passed iterable

    Examples:

    >>> list(argunique('AAAABBBCCDAABBB'))
    [0, 4, 7, 9]
    >>> list(argunique('ABbcCAD', key=str.lower))
    [0, 1, 3, 6]
    >>> list(argunique([]))
    []
    >>> list(argunique(range(10), key=type))
    [0]
    >>> unhashable = [{'value': n, 'even': n % 2 == 0} for n in range(1, 10)]
    >>> import operator
    >>> list(argunique(unhashable, key=operator.itemgetter('even')))
    [0, 1]

    """
    return (index for index, _ in enumerate_unique(iterable, key=key))


def allunique(iterable: Iterable[Any]) -> bool:
    """Check whether all items of an iterable are distinct.

    Works for either hashable or unhashable items. If all items are
    hashable, allunique_hashable() will be much faster.

    Returns True for an empty iterable. Will not return if passed an
    infinite iterator.

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

    Returns True for an empty iterable. Will not return if passed an
    infinite iterator.

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
