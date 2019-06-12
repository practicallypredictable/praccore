"""Functions that are imported by other modules in this sub-package.

Avoids circular imports and eases maintainability.

"""
import collections
import functools
import itertools

from typing import (
    Any,
    Collection,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    Union,
)

from litecore.sentinels import NO_VALUE as _NO_VALUE

from litecore.irecipes.typealiases import (
    KeyFunc,
    FilterFunc,
)


def peek(
    iterable: Iterable[Any],
    *,
    default: Optional[Any] = None,
) -> Tuple[Any, Iterator[Any]]:
    """Allow a peek at first item of an iterator, without consuming it.

    Arguments:
        iterable: object to be peeked at

    Keyword Arguments:
        default: value to return if iterable is empty

    Returns:
        tuple consisting of the first item, and an iterator equivalent
        to the original iterable

    Examples:

    >>> items = range(5)
    >>> head, it = peek(items)
    >>> head
    0
    >>> list(it)
    [0, 1, 2, 3, 4]
    >>> head, it = peek([])
    >>> head is None
    True
    >>> len(list(it))
    0

    """
    iterator = iter(iterable)
    try:
        head = next(iterator)
    except StopIteration:
        return default, iterable
    return head, itertools.chain([head], iterator)


def consume(
        iterator: Iterator[Any],
        *,
        items: Optional[int] = None,
) -> None:
    """Consume (and discard) items of an iterator.

    Without the optional items keyword argument, consumes all of the
    iterator quickly. With items specified, consumes at most that many
    items of the iterator. If the iterator has fewer items than the
    specified number, the iterator will be fully consumed.

    Arguments:
        iterator: generic iterator

    Keyword Arguments:
        items: number of items to consume (optional; default is None,
            signifying that the entire iterator should be consumed)

    Returns:
        None

    Examples:

    >>> it = (n for n in range(10))
    >>> next(it)
    0
    >>> consume(it, items=3)
    >>> next(it)
    4
    >>> consume(it, items=7)
    >>> next(it)
    Traceback (most recent call last):
     ...
    StopIteration

    """
    if items is None:
        collections.deque(iterator, maxlen=0)
    else:
        next(itertools.islice(iterator, items, items), None)


def take(
        items: int,
        iterable: Iterable[Any],
        *,
        factory: Type[Collection] = list,
) -> Collection[Any]:
    """Return a collection of a specified number of items of an iterable.

    The returned collection by default is a list. Other possibilities
    include tuple, set, collections.OrderedDict.fromkeys, collections.deque
    or custom-defined collection types.

    The returned collection will be initialized by calling its constructor
    with an iterable of length min(len(iterable), items).

    If the iterable is an iterator, the specified number of items of the
    iterator will be consumed.

    Arguments:
        items: non-negative number of items to be consumed and returned
        iterable: object from which items are to be taken

    Keyword Arguments:
        factory: type of collection to return (default is list)

    Returns:
        collection defined by the first items of iterable

    Examples:

    >>> take(1, range(5))
    [0]
    >>> take(2, range(5))
    [0, 1]
    >>> take(0, range(5), factory=tuple)
    ()
    >>> take(6, iter(range(5)), factory=set)
    {0, 1, 2, 3, 4}
    >>> take(5, iter(()))
    []

    """
    return factory(itertools.islice(iterable, items))


def drop(
        items: int,
        iterable: Iterable[Any],
) -> Iterator[Any]:
    """Return iterator of an iterable skipping specified number of items.

    If the passed iterable does not have the specified number of items,
    the returned iterator will have no items.

    If the passed iterable is an iterator, its initial items will be
    consumed.

    Arguments:
        items: non-negative number of items to skip
        iterable: object to be acted upon

    Returns:
        iterator skipping the specified number of items

    Examples:

    >>> list(drop(1, range(5)))
    [1, 2, 3, 4]
    >>> list(drop(2, range(5)))
    [2, 3, 4]
    >>> list(drop(0, range(5)))
    [0, 1, 2, 3, 4]
    >>> list(drop(6, range(5)))
    []

    """
    return itertools.islice(iterable, items, None)


def pairwise(iterable: Iterable[Any]) -> Iterator[Tuple[Any, Any]]:
    """Return iterator of overlapping pairs of items from an iterable.

    Will return an empty iterable if the passed iterable does not have
    at least two items.

    Will not return if passed an infinite iterator.

    Arguments:
        iterable: object to be iterated over pairwise

    Returns:
        iterator of tuples of pairs of sequential items from iterable

    Examples:

    >>> list(pairwise(range(8)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
    >>> list(pairwise(range(1)))
    []
    >>> list(pairwise(()))
    []

    """
    first, second = itertools.tee(iterable)
    next(second, None)
    return zip(first, second)


def window(
        items: int,
        iterable: Iterable[Any],
) -> Iterator[Tuple[Any, ...]]:
    """Return iterator of moving window of items from original iterable.

    If the window length extends beyond the last item of the iterable,
    return an empty iterable.

    Arguments:
        items: number of items to include in each window
        iterable: object to be iterated over

    Returns:
        iterator of tuples of pairs of sequential items from iterable

    Examples:

    >>> list(window(3, range(5)))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
    >>> list(window(4, range(3)))
    []

    """
    iterator = iter(iterable)
    window = tuple(itertools.islice(iterator, items))
    if len(window) == items:
        yield window
    for item in iterator:
        window = window[1:] + (item,)
        yield window


def window_padded(
        items: int,
        iterable: Iterable[Any],
        *,
        start: int = 0,
        step: int = 1,
        fillvalue: Any = None,
) -> Iterator[Tuple[Any, ...]]:
    """Return iterator of moving windows from iterable, padding if needed.

    Similar to window(), with the addition of keyword arguments for
    specifying padding, start point and step size.

    If the start point of the windowing is beyond the last item in the
    iterable, return an empty tuple.

    Arguments:
        items: number of items to include in each window
        iterable: object to be iterated over

    Keyword Arguments:
        start: index into iterable of where to start windowing
            (optional; defaults to 0, the beginning of the iterable)
        step: step size for each move of the window
            (optional; defaults to 1)
        fillvalue: default value to use if the window extends beyond end
            of the iterable (optional; default is None)

    Returns:
        iterator of tuples of pairs of sequential items from iterable

    Examples:

    >>> list(window_padded(3, range(5)))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
    >>> list(window_padded(3, range(6), step=2))
    [(0, 1, 2), (2, 3, 4), (4, 5, None)]
    >>> list(window_padded(4, range(3)))
    [(0, 1, 2, None)]
    >>> list(window_padded(3, range(6), start=2, step=2))
    [(2, 3, 4), (4, 5, None)]
    >>> list(window_padded(4, range(3), start=5))
    []

    """
    if items <= 0:
        msg = f'items must be positive'
        raise ValueError(msg)
    if step <= 0:
        msg = f'step must be positive'
        raise ValueError(msg)
    iterator = iter(iterable)
    if start > 0:
        # Move to the start point, ignore the values
        consume(iterator, items=start)
        item, iterator = peek(iterator, default=_NO_VALUE)
        if item is _NO_VALUE:
            # We started past the end of the original iterable
            # So return empty tuple
            return ()
    elif start < 0:
        msg = f'start must be non-negative'
        raise ValueError(msg)

    window = collections.deque([], maxlen=items)
    window_append = window.append

    # The initial window
    for _ in range(items):
        window_append(next(iterator, fillvalue))
    yield tuple(window)

    # Now all of the additional windows that contain regular values
    # Initialize index here in case iterator was already consumed
    index = None
    for index, item in enumerate(iterator, start=1):
        window_append(item)  # The old values fall out one at a time
        if index % step == 0:
            yield tuple(window)

    # The final window with padded values
    # Variable index will not be None if enumerate consumed additional items
    if index:
        extras = index % step
        fillers = step - extras
        if extras and (fillers < items):
            for _ in range(fillers):
                window_append(fillvalue)
            yield tuple(window)


def take_batches(
        iterable: Iterable[Any],
        *,
        length: int,
        fillvalue: Any = _NO_VALUE,
        factory: Optional[Type[Collection]] = None,
) -> Iterator[Collection[Any]]:
    """Break an iterable into iterator of collections of specified length.

    The returned collection by default is a tuple. Other possibilities
    include list, set, collections.OrderedDict.fromkeys, collections.deque
    or custom-defined collection types.

    If the iterable is of a length not evenly divisible by the batch
    length, the last list item of the returned iterator will be shorter
    than the specified length.

    Use this function to break computations on large collections of items
    into smaller batches.

    Arguments:
        iterable: object from which items are to be taken

    Keyword Arguments:
        length: non-negative number of items to be consumed and returned
        factory: type of collection to return
            (optional; default is None, same as specifying tuple)

    Returns:
        iterator of collections of specified length (or shorter for the
        last item of the collection)

    Examples:

    >>> list(take_batches(range(8), length=3))
    [range(0, 3), range(3, 6), range(6, 8)]
    >>> list(take_batches(range(8), length=3, factory=list))
    [[0, 1, 2], [3, 4, 5], [6, 7]]
    >>> list(take_batches(list(range(8)), length=3))
    [[0, 1, 2], [3, 4, 5], [6, 7]]
    >>> list(take_batches(list(range(8)), length=3, fillvalue='boo!'))
    [(0, 1, 2), (3, 4, 5), (6, 7, 'boo!')]
    >>> cycle = [1, 2, 3, 4] * 2
    >>> list(take_batches(cycle, length=3, fillvalue='boo!', factory=tuple))
    [(1, 2, 3), (4, 1, 2), (3, 4, 'boo!')]
    >>> list(take_batches(iter(range(8)), length=3))
    [(0, 1, 2), (3, 4, 5), (6, 7)]
    >>> list(take_batches(iter(range(8)), length=10))
    [(0, 1, 2, 3, 4, 5, 6, 7)]
    >>> list(take_batches(iter(cycle), length=10, factory=set))
    [{1, 2, 3, 4}]
    >>> list(take_batches([], length=3))
    []
    >>> list(take_batches('ABCDEFG', length=3, fillvalue=None))
    [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', None, None)]

    """
    if fillvalue is not _NO_VALUE:
        groups = [iter(iterable)] * length
        batches = itertools.zip_longest(*groups, fillvalue=fillvalue)
    else:
        _factory = tuple if factory is None else factory
        empty = _factory()
        try:
            iterable[0]
        except TypeError:
            batches = iter(
                functools.partial(
                    take,
                    length,
                    iter(iterable),
                    factory=_factory,
                ),
                empty,
            )
        except IndexError:
            return iter(empty)
        else:
            start_indices = itertools.count(0, length)
            slices = (iterable[i: i + length] for i in start_indices)
            batches = itertools.takewhile(bool, slices)
    if factory is not None:
        return (factory(batch) for batch in batches)
    else:
        return batches


def keyed_items(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Tuple[Any, Any]]:
    """Return iterator of tuples of items and key values of an iterable.

    Given an iterable of values and an (optional) key function, return
    an iterator of 2-tuples for each item, with the first being the
    value of the key function applied to the item, and the second being
    the item unmodified. If the key function is None, the original item
    value is used as the key.

    This is used elsewhere in this package as an alternative to using
    lambda expressions for optional key functions. It's generally better
    to replace the original iterable with a generator expression rather
    than calling a lambda function (particuarly a "null" expression
    such as lambda x: x) in a tight loop.

    Arguments:
        iterable: object with items to be keyed

    Keyword Arguments:
        key: single-argument callable key function
            (optional; defaults to None)

    Returns:
        iterator of 2-tuples, the first item of each being the key and
        the second item of each being the original item value

    Examples:

    >>> parity = lambda x: 'even' if x % 2 == 0 else 'odd'
    >>> list(keyed_items(range(5), key=parity))
    [('even', 0), ('odd', 1), ('even', 2), ('odd', 3), ('even', 4)]
    >>> list(keyed_items('AbcDe'))
    [('A', 'A'), ('b', 'b'), ('c', 'c'), ('D', 'D'), ('e', 'e')]
    >>> list(keyed_items('AbcDe', key=lambda s: s.lower()))
    [('a', 'A'), ('b', 'b'), ('c', 'c'), ('d', 'D'), ('e', 'e')]

    """
    if key is not None:
        return ((key(x), x) for x in iterable)
    else:
        return ((x, x) for x in iterable)


def flag_where(
        where: Union[FilterFunc, Any],
        iterable: Iterable[Any],
        *,
        maxflags: Optional[int] = None,
) -> Iterator[Any]:
    """Return iterator of tuples of items and truth values of an iterable.

    Given an iterable of values and a condition, return an iterator of
    2-tuples for each item, with the first being the value True or False,
    and the second being the item unmodified.

    The condition is either a value or a single-argument callable which
    returns a boolean value. If a value is specified, items equalling
    that value will test True. If a callable is specified, it will be
    called with each item as argument and the return value used as the
    truth value for that item.

    The optional maxflags argument specifies a limit on the number of
    values which may be flagged as True.

    This is used elsewhere in this package as an alternative to using
    lambda expressions for optional key functions. It's generally better
    to replace the original iterable with a generator expression rather
    than calling a lambda function (particuarly a "null" expression
    such as lambda x: x) in a tight loop.

    Arguments:
        where: either a value, or a single-argument callable which
            returns a boolean value
        iterable: object with items to be flagged True or False

    Keyword Arguments:
        maxflags: maximum number of values to flag as True
            (optional; defaults to None, signifying no limit)

    Returns:
        iterator of 2-tuples, the first item of each being the truth
        value of the item (or False, if any maxflags limit has been
        hit), the second item of each being the original item value.

    Raises:
        ValueError: if maxflags is specified and less than 1

    Examples:

    >>> items = [0, 1, 2, 5, 4]
    >>> list(flag_where(2, items))
    [(False, 0), (False, 1), (True, 2), (False, 5), (False, 4)]
    >>> list(flag_where(lambda x: x % 2 == 0, items))
    [(True, 0), (False, 1), (True, 2), (False, 5), (True, 4)]
    >>> list(flag_where(lambda x: x % 2 == 0, items, maxflags=2))
    [(True, 0), (False, 1), (True, 2), (False, 5), (False, 4)]

    """
    if maxflags is None:
        if callable(where):
            return ((True, x) if where(x) else (False, x) for x in iterable)
        else:
            return ((True, x) if x == where else (False, x) for x in iterable)
    else:
        if maxflags < 1:
            raise ValueError('maxflags must be positive')
        flags = 0

        if callable(where):
            def func(x):
                nonlocal flags
                if where(x) and flags < maxflags:
                    flags += 1
                    return (True, x)
                else:
                    return (False, x)
        else:
            def func(x):
                nonlocal flags
                if x == where and flags < maxflags:
                    flags += 1
                    return (True, x)
                else:
                    return (False, x)
        return map(func, iterable)
