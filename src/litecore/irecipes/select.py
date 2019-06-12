"""Functions for selecting items from an iterable.

"""
import collections
import itertools

from typing import (
    Any,
    Iterable,
    Iterator,
    Optional,
)

from litecore.irecipes.typealiases import (
    FilterFunc,
)


def only_one(iterable: Iterable[Any]) -> Any:
    """Consume and return first and only item of an iterable.

    If the iterable has exactly one item, return that item, otherwise raise
    an exception.

    Arguments:
        iterable: iterator or collection expected to contain only one item

    Returns:
        single item of iterable

    Raises:
        ValueError: the iterable is empty or has more than one item

    Examples:

    >>> only_one([])
    Traceback (most recent call last):
     ...
    ValueError: expected 1 item, got empty iterable
    >>> only_one(['test'])
    'test'
    >>> only_one(['this', 'should', 'fail'])
    Traceback (most recent call last):
     ...
    ValueError: expected only 1 item in iterable
    """
    iterator = iter(iterable)
    try:
        value = next(iterator)
    except StopIteration:
        msg = f'expected 1 item, got empty iterable'
        raise ValueError(msg)
    try:
        next(iterator)
    except StopIteration:
        return value
    else:
        msg = f'expected only 1 item in iterable'
        raise ValueError(msg)


def first(
        iterable: Iterable[Any],
        *,
        key: Optional[FilterFunc] = None,
        default: Optional[Any] = None,
) -> Any:
    """Return first item of an iterable for which a condition is true.

    The default condition is to just return the first item in the iterable
    (i.e., the implicit condition is that the item exists). Pass the bool
    constructor if you just want to return the first "truthy" value.

    If the iterable is empty, or no value is found matching the desired
    condition, return the default value.

    If the iterable is an iterator, its items up to and including the first to
    test True will be consumed.

    Arguments:
        iterable: iterator or collection of items to be tested for condition

    Keyword Arguments:
        key: single-argument callable defining condition to be tested
            (optional; default is None)
        default: value to return if the passed iterable is empty, or there is
            no item for which the condition is True (optional; default is None)

    Returns:
        first item of the passed iterable meeting the specified condition,
        otherwise the default value if there is no such item

    Examples:

    >>> first([]) is None
    True
    >>> first([], default='missing')
    'missing'
    >>> items = [False, None, 0, '', (), len, 1, 2, 3, 4]
    >>> first(items)
    False
    >>> first(items[:5], key=bool) is None
    True
    >>> first(items[:5], key=bool, default='missing')
    'missing'
    >>> first(items, key=bool)
    <built-in function len>
    >>> first(range(1, 3), key=lambda x: x % 2 == 0)
    2
    >>> first(range(1, 3), key=lambda x: x < 1, default='missing')
    'missing'
    >>> first(items, key=lambda x: type(x) is int)
    0
    >>> it = iter(items)
    >>> first(it, key=bool)
    <built-in function len>
    >>> list(it)
    [1, 2, 3, 4]

    """
    items = iterable if key is None else filter(key, iterable)
    return next(iter(items), default)


def nth(
        item: int,
        iterable: Iterable[Any],
        *,
        key: Optional[FilterFunc] = None,
        default: Optional[Any] = None,
) -> Any:
    """Return nth item of an iterable for which a condition is true.

    The default condition is to just return the nth item in the iterable
    (i.e., the implicit condition is that the item exists). Pass the bool
    constructor if you just want to return the nth "truthy" value.

    If the iterable is empty, or no value is found matching the desired
    condition, return the default value.

    If the iterable is an iterator, its items up to and including the nth to
    test True will be consumed.

    Item counting starts with 0, as is usual for Python indexing.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable defining condition to be tested
            (optional; default is None)
        default: value to return if the passed iterable is empty, or there is
            no item for which the condition is True
            (optional; default is None)

    Returns:
        specified item number of the passed iterable, or, if the iterable is
        empty or no item matches the condition, the default value

    Examples:

    >>> nth(3, []) is None
    True
    >>> nth(3, [], default='missing')
    'missing'
    >>> items = [False, None, 0, '', (), len, 1, 2, 3, 4]
    >>> nth(3, items)
    ''
    >>> nth(3, items[:5], key=bool) is None
    True
    >>> nth(3, items[:5], key=bool, default='missing')
    'missing'
    >>> nth(3, items, key=bool)
    3
    >>> nth(0, items, key=bool) == first(items, key=bool)
    True
    >>> nth(1, range(10), key=lambda x: x % 2 == 0)
    2
    >>> nth(3, range(10), key=lambda x: x % 2 == 0)
    6
    >>> it = iter(items)
    >>> nth(3, it, key=bool)
    3
    >>> list(it)
    [4]

    """
    if key is None:
        try:
            return iterable[item]
        except IndexError:
            return default
        except TypeError:
            return next(itertools.islice(iterable, item, None), default)
    else:
        iterator = filter(key, iterable)
        return next(itertools.islice(iterator, item, None), default)


def tail(items: int, iterable: Iterable[Any]) -> Iterator:
    """Return iterator over the last specified number of items of iterable.

    If the number of items exceeds the length of the iterable, every item
    of the iterable will be contained in the resulting iterator.

    If the given iterable is an iterator, it will be fully consumed.

    Arguments:
        items: non-negative number of items to be returned as output
        iterable: object to be acted upon

    Returns:
        iterator of the last items in the iterable

    Examples:

    >>> list(tail(2, range(10)))
    [8, 9]
    >>> list(tail(11, range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> it = iter(range(10))
    >>> list(tail(2, it))
    [8, 9]
    >>> len(list(it))
    0
    >>> list(tail(2, it))
    []

    """
    try:
        return iter(iterable[-items:])
    except TypeError:
        return iter(collections.deque(iterable, maxlen=items))


def last(
        iterable: Iterable[Any],
        *,
        default: Optional[Any] = None,
) -> Any:
    """Return the last item of an iterable.

    If the iterable is empty, return the default value.

    If the given iterable is an iterator, it will be fully consumed.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        default: value to return if the iterable is emtpy
            (optional; defaults to None)

    Returns:
        the last item in the iterable, or, if the iterator is empty,
        the default value

    Examples;

    >>> last(range(10))
    9
    >>> last([]) is None
    True
    >>> last(c for c in '') is None
    True
    >>> last(c for c in 'abc') == 'c'
    True
    >>> it = iter(range(10))
    >>> last(it)
    9
    >>> len(list(it))
    0

    """
    try:
        return iterable[-1]
    except IndexError:
        return default
    except TypeError:
        result = collections.deque(iterable, maxlen=1)
        if result:
            return result[0]
        else:
            return default


def except_last(iterable: Iterable[Any]) -> Iterator:
    """Return iterator over all the items of an iterable except the last.

    Equivalent to iterable[:-1] for a sequence. If the iterable is an iterator,
    it will be consumed and the last item will be discarded.

    Arguments:
        iterable: iterator or collection of items

    Yields:
        each item in iterable other than the last

    Examples:

    >>> list(except_last(range(5)))
    [0, 1, 2, 3]
    >>> list(except_last([]))
    []
    >>> it = except_last(iter(range(5)))
    >>> list(it)
    [0, 1, 2, 3]
    >>> next(it)
    Traceback (most recent call last):
     ...
    StopIteration

    """
    try:
        yield from iterable[:-1]
    except IndexError:
        return iter(())
    except TypeError:
        iterator = iter(iterable)
        try:
            item = next(iterator)
        except StopIteration:
            return iter(())
        while True:
            prev = item
            try:
                item = next(iterator)
            except StopIteration:
                break
            else:
                yield prev
