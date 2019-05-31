"""Various functions which process one or more iterables.

Many functions/generators yield items from or return a modified iterator.

"""
import collections
import functools
import itertools
import operator

from typing import (
    Any,
    Callable,
    Collection,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from litecore.sentinels import NO_VALUE as _NO_VALUE

KeyFunc = Callable[[Any], Any]
FilterFunc = Callable[[Any], bool]


def iter_with(context_manager: Iterable[Any]) -> Iterator:
    """Wrap an iterable context manager so it closes when consumed.

    Allows a context manager which is also iterable to be used lazily or
    asynchronously. Whatever resources are used by the context manager will
    be released automatically when the iterator is consumed.

    Arguments:
        context_manager: context manager which is also an iterable

    Yields:
        each item of the iterable

    """
    with context_manager as iterable:
        for item in iterable:
            yield item


def consume(
        iterator: Iterator[Any],
        *,
        items: Optional[int] = None,
) -> None:
    """Consume (and discard) items of an iterator.

    Without the optional items keyword argument, consumes all of the iterator
    quickly. With items specified, consumes at most that many items of the
    iterator. If the iterator has fewer items than the specified number, the
    iterator will be fully consumed.

    Arguments:
        iterator: generic iterator

    Keyword Arguments:
        items: number of items to consume (optional; default is None)

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


def drop(
        items: int,
        iterable: Iterable[Any],
) -> Iterator[Any]:
    """Return iterator of an iterable skipping the specified number of items.

    If the passed iterable does not have the specified number of items, the
    returned iterator will have no items.

    Arguments:
        items: non-negative number of items to skip
        iterable: object to be acted upon

    Returns:
        Iterator skipping the specified number of items

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
    >>> last(c for c in 'abc') is 'c'
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


def unique_with_index(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Tuple[int, Any]]:
    """Return iterator of unique items from an iterable, along with item index.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided, will be
    called to produce a modified value for each item prior to determining
    uniqueness. Only items with different keys will compare as different. The
    default is None, which means that each item is tested for uniqueness
    without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None)

    Yields:
        2-tuples of unique values in the order they were encountered and the
        index of each item in the passed iterable

    >>> list(unique_with_index('AAAABBBCCDAABBB'))
    [(0, 'A'), (4, 'B'), (7, 'C'), (9, 'D')]
    >>> list(unique_with_index('ABbcCAD', key=str.lower))
    [(0, 'A'), (1, 'B'), (3, 'c'), (6, 'D')]
    >>> list(unique_with_index([]))
    []
    >>> list(unique_with_index(range(10), key=type))
    [(0, 0)]
    >>> unhashable = [{'value': n, 'even': n % 2 == 0} for n in range(1, 10)]
    >>> import operator
    >>> list(unique_with_index(unhashable, key=operator.itemgetter('even')))
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
) -> Iterator:
    """Return iterator of unique items from an iterable.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided, will be
    called to produce a modified value for each item prior to determining
    uniqueness. Only items with different keys will compare as different. The
    default is None, which means that each item is tested for uniqueness
    without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None)

    Yields:
        each unique value in the iterable in the order it is occurs in the
        passed iterable

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
    for index, item in unique_with_index(iterable, key=key):
        yield item


def argunique(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[int]:
    """Return iterator of indices of unique items from an iterable.

    The items in the iterable may be hashable or unhashable.

    The optional key is a single-argument callable that, if provided, will be
    called to produce a modified value for each item prior to determining
    uniqueness. Only items with different keys will compare as different. The
    default is None, which means that each item is tested for uniqueness
    without modification.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None)

    Yields:
        indices of each unique value in the iterable in the order it is
        occurs in the passed iterable

    Note:
        Will not return if passed an infinite iterator.
        Calls unique_with_index() but only yields item indices, not values

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
    for index, item in unique_with_index(iterable, key=key):
        yield index


def take(
        items: int,
        iterable: Iterable[Any],
        *,
        factory: Type[Collection[Any]] = list,
) -> Collection[Any]:
    """Return a collection of a specified number of items of an iterable.

    The returned collection by default is a list. Other possibilities include
    tuple, set, collections.OrderedDict.fromkeys, collections.deque or
    custom-defined collection types.

    The returned collection will be initialized by calling its constructor
    with an iterable of length min(len(iterable), items).

    If the iterable is an iterator, the specified number of items of the
    iterator will be consumed.

    Arguments:
        items: non-negative number of items to be consumed and returned
        iterable: iterator or collection of items

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


def take_specified(
    iterable: Iterable[Any],
    *,
    indices: Collection[int],
    factory: Type[Collection[Any]] = list,
) -> Iterator[Any]:
    """Return a collection of specified items from an iterable.

    The indices keyword argument specifies which items of the iterable should
    be returned in a collection of type specified by the factory keyword
    argument (the default is a list). See the take() function for examples
    of other possible factory types.

    If the iterable is an iterator, the number of items of the iterator
    consumed will be the maximum specified index.

    An IndexError will be raised if one of the specified indices is invalid
    for the passed iterable.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        indices: collection of indices to extract from iterable
        factory: type of collection to return (default is list)

    Returns:
        collection defined by the specified items of iterable

    Examples:

    >>> data = list(reversed(range(10)))
    >>> take_specified(data, indices=[1, 3, 5])
    [8, 6, 4]
    >>> it = iter(data)
    >>> take_specified(it, indices={1, 3, 5})
    [8, 6, 4]
    >>> list(it)
    [3, 2, 1, 0]
    >>> take_specified(range(1, 11), indices=(1, 3, 5), factory=set)
    {2, 4, 6}
    >>> take_specified(data, indices=(1, 11))
    Traceback (most recent call last):
     ...
    IndexError: list index out of range

    """
    try:
        return factory(iterable[i] for i in indices)
    except TypeError:
        items = take(max(indices) + 1, iterable)
        return factory(items[i] for i in indices)


def take_while_index(
        predicate: FilterFunc,
        iterable: Iterable[Any],
        *,
        start: int = 0,
) -> Iterator[Any]:
    """

    Examples:

    >>> odd = lambda n: n % 2 != 0
    >>> list(take_while_index(odd, range(10)))
    [1, 3, 5, 7, 9]

    """
    for i, item in enumerate(iterable, start):
        if predicate(i):
            yield item


def take_batches(
        iterable: Iterable[Any],
        *,
        length: int,
        fillvalue: Any = _NO_VALUE,
        factory: Optional[Type[Collection]] = None,
) -> Iterator[Collection[Any]]:
    """Break an iterable into an iterator of collections of specified length.

    The returned collection by default is a tuple. Other possibilities include
    list, set, collections.OrderedDict.fromkeys, collections.deque or
    custom-defined collection types.

    If the iterable is of a length not evenly divisible by the batch length,
    the last list item of the returned iterator will be shorter than the
    specified length.

    Use this function to break computations on large collections of items
    into smaller batches.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        length: non-negative number of items to be consumed and returned
        factory: type of collection to return
            (optional; default is None, which is the same as specifying tuple)

    Returns:
        iterator of collections of specified length (or shorter for the last)

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


def peek(
    iterable: Iterable[Any],
    *,
    default: Optional[Any] = None,
) -> Tuple[Any, Iterator]:
    """Allow a peek at first item of an iterator, without consuming it.

    Arguments:
        iterable: object to be peeked at

    Keyword Arguments:
        default: value to return if iterable is empty
    Returns:
        tuple of the first item and an iterator equivalent to the original

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


def prepend(
        value: Any,
        iterable: Iterable[Any],
        *,
        times: int = 1,
) -> Iterator:
    """Return an iterator with a specified value prepended.

    Arguments:
        value: the value to prepend to the iterable
        iterable: the iterable to which the value is to be prepended

    Keyword Arguments:
        times: number of times to prepend the value (optional; default is 1)

    Returns:
        iterable combining the prepended value and the original iterable

    Examples:

    >>> list(prepend(-1, range(5)))
    [-1, 0, 1, 2, 3, 4]
    >>> list(prepend('hi ho', ['off to work we go'], times=2))
    ['hi ho', 'hi ho', 'off to work we go']

    """
    return itertools.chain([value] * times, iterable)


def pad(
        iterable: Iterable[Any],
        *,
        value: Any = None,
        times: Optional[int] = None,
) -> Iterator:
    """Return iterator of original iterable followed by specified padding.

    Default behavior is to add an infinite number of None objects on the end
    of the provided iterable; however both the object to be added and the
    number of times can be modified by the keyword arguments.

    Arguments:
        iterable: object to be padded

    Keyword Arguments:
        value: object to be added at the end (optional; default is None)
        times: number of times to pad (optional; default is None)

    Examples:

    >>> list(pad(range(5), times=3))
    [0, 1, 2, 3, 4, None, None, None]
    >>> list(pad(['baby shark'], value='do', times=6))
    ['baby shark', 'do', 'do', 'do', 'do', 'do', 'do']

    """
    return itertools.chain(iterable, itertools.repeat(value, times=times))


def finite_cycle(
        times: int,
        iterable: Iterable[Any],
) -> Iterator:
    """Return iterator cycling through a given iterable finitely-many times.

    The passed iterable is assumed to be finite.

    Arguments:
        times: integral number of times to repeat the iterable
        iterable: finite iterable to be repeated

    Returns:
        iterator repeating the passed iterable the specified number of times

    Examples:

    >>> pattern = 'hee haw'.split()
    >>> list(finite_cycle(3, pattern))
    ['hee', 'haw', 'hee', 'haw', 'hee', 'haw']

    """
    repeated = itertools.repeat(tuple(iterable), times)
    return itertools.chain.from_iterable(repeated)


def enumerate_cycle(
        iterable: Iterable[Any],
        *,
        times: Optional[int] = None,
):
    iterable = tuple(iterable)
    if not iterable:
        return iter(())
    counter = itertools.count() if times is None else range(times)
    return ((i, item) for i in counter for item in iterable)


def round_robin(*iterables) -> Iterator:
    """Return iterator yielding from each iterable in turn.

    Stop when the last item from the shortest iterable is yielded.

    Arguments:
        an arbitrary number of iterable positional arguments

    Returns:
        Iterator rotating among iterables until shortest is exhausted.

    Examples:

    >>> numbers = range(3)
    >>> chars = 'abcde'
    >>> classes = [int, str, dict, list]
    >>> list(round_robin(numbers, chars, classes))
    [0, 'a', <class 'int'>, 1, 'b', <class 'str'>, 2, 'c', <class 'dict'>]

    """
    return itertools.chain.from_iterable(zip(*iterables))


def round_robin_longest(*iterables) -> Iterator:
    """Return iterator yielding from each iterable in turn.

    Continue until all iterables have been consumed. As each iterable is
    consumed, it falls out of the rotation.

    Arguments:
        an arbitrary number of iterable positional arguments

    Returns:
        an iterator rotating among iterable arguments until all are exhausted

    Examples:

    >>> numbers = range(3)
    >>> chars = 'abcde'
    >>> classes = [int, str, dict, list]
    >>> list(round_robin_longest(numbers, chars, classes))  # doctest: +ELLIPSIS
    [0, 'a', ... 2, 'c', <class 'dict'>, 'd', <class 'list'>, 'e']

    """
    zipped = itertools.zip_longest(*iterables, fillvalue=_NO_VALUE)
    chained = itertools.chain.from_iterable(zipped)
    return itertools.filterfalse(lambda item: item is _NO_VALUE, chained)


def rotate_cycle(
        iterable: Iterable[Any],
) -> Iterator[Tuple[Any, ...]]:
    """

    >>> take(5, rotate_cycle(range(4)))
    [(0, 1, 2, 3), (1, 2, 3, 0), (2, 3, 0, 1), (3, 0, 1, 2), (0, 1, 2, 3)]

    """
    items = list(iterable)
    return window(len(items), itertools.cycle(items))


def intersperse(
        value: Any,
        iterable: Iterable[Any],
        *,
        spacing: int = 1,
) -> Iterator:
    """Introduce a value between items of an iterable.

    The default behavior is to introduce the value between every item of the
    iterable. This can be altered by providing the spacing keyword argument.

    The iterator's last item will be the last item of the original iterable.

    Arguments:
        value: the value to introduced
        iterable: collection or iterator of items

    Keyword Arguments:
        spacing: positive number of items from the original iterable between
            each instance of the introduced value

    Returns:
        iterator with the value introduced between items of original iterable

    >>> list(intersperse('hi', range(5)))
    [0, 'hi', 1, 'hi', 2, 'hi', 3, 'hi', 4]
    >>> list(intersperse('hi', range(5), spacing=2))
    [0, 1, 'hi', 2, 3, 'hi', 4]
    >>> list(intersperse('hi', range(4), spacing=2))
    [0, 1, 'hi', 2, 3]

    """
    if spacing == 1:
        filler = itertools.repeat(value)
        return drop(1, round_robin(filler, iterable))
    elif spacing > 1:
        filler = itertools.repeat([value])
        batches = take_batches(iterable, length=spacing)
        chain = drop(1, round_robin(filler, batches))
        return itertools.chain.from_iterable(chain)
    else:
        msg = f'spacing argument must be positive'
        raise ValueError(msg)


def partition(
        iterable: Iterable[Any],
        *,
        by: Callable[[Any], bool],
) -> Tuple[Iterator, Iterator]:
    """Split an iterable into two iterators based upon a condition.

    Returns two iteators, one for which the condition is False, and one for
    which the condition is True.

    The condition is specified by the required keyword argument by, which just
    be a callable returning True or False based upon the value of one argument.
    It will be called for each item in the iterable in sequence.

    Arguments:
        iterable: object for which items are to be partitioned

    Keyword Arguments:
        by: callable which takes one argument and returns a bool

    Returns:
        A tuple of two iterators, the first of which iterates over all items of
        the original iterable for which the condition is False, and the other
        for whihc the condition is True.

    Note:
        * Will not return if passed an infinite iterator.

    Examples:

    >>> odd, even = partition(range(10), by=lambda n: n % 2 == 0)
    >>> list(odd)
    [1, 3, 5, 7, 9]
    >>> list(even)
    [0, 2, 4, 6, 8]
    >>> text = 'We hold these truths to be self-evident'.split()
    >>> short, long = partition(text, by=lambda s: len(s) > 4)
    >>> list(short)
    ['We', 'hold', 'to', 'be']
    >>> list(long)
    ['these', 'truths', 'self-evident']

    """
    false_it, true_it = itertools.tee(iterable)
    return (itertools.filterfalse(by, false_it), filter(by, true_it))


def split(
        iterable: Iterable[Any],
        *,
        at: int,
):
    first, second = itertools.tee(iterable)
    return itertools.islice(first, at), itertools.islice(second, at, None)


def take_then_split(
        iterable: Iterable[Any],
        *,
        until: Callable,
):
    first, second = itertools.tee(iterable)
    return itertools.takewhile(until, first), itertools.dropwhile(until, second)


def split_after(
        iterable: Iterable[Any],
        *,
        each_time: Callable,
):
    cache = []
    for item in iterable:
        cache.append(item)
        if each_time(item) and cache:
            yield cache
            cache = []
    if cache:
        yield cache


def split_before(iterable, *, each_time: Callable):
    cache = []
    for item in iterable:
        if each_time(item) and cache:
            yield cache
            cache = []
        cache.append(item)
    yield cache


def window(
        items: int,
        iterable: Iterable[Any],
        *,
        start: int = 0,
        step: int = 1,
        fillvalue: Any = None,
) -> Iterator[Tuple[Any, ...]]:
    """Return iterator of moving window of items from original iterable.

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
        fillvalue: default value to use if the window extends beyond end of
            the iterable (optional; default is None)
    Returns:
        Iterator of tuples of pairs of sequential items from iterable

    Note:
        * Will not return if passed an infinite iterator.

    Examples:

    >>> list(window(3, range(5)))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
    >>> list(window(3, range(6), step=2))
    [(0, 1, 2), (2, 3, 4), (4, 5, None)]
    >>> list(window(4, range(3)))
    [(0, 1, 2, None)]
    >>> list(window(3, range(6), start=2, step=2))
    [(2, 3, 4), (4, 5, None)]
    >>> list(window(4, range(3), start=5))
    []

    """
    if items <= 0:
        msg = f'Got items argument {items!r}; must be positive'
        raise ValueError(msg)
    if step <= 0:
        msg = f'Got step argument {step!r}; must be positive'
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
        msg = f'Got start argument {start!r}; cannot be negative'
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


def pairwise(iterable: Iterable[Any]) -> Iterator:
    """Return iterator of overlapping pairs of items from original iterable.

    Arguments:
        iterable: object to be iterated over pairwise

    Returns:
        Iterator of tuples of pairs of sequential items from iterable

    Note:
        * Will not return if passed an infinite iterator.

    Examples:

    >>> list(pairwise(range(8)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]

    """
    first, second = itertools.tee(iterable)
    next(second, None)
    return zip(first, second)


def replace(
        iterable: Iterable[Any],
        *,
        where: Union[Callable[[Any], bool], Iterable, Any],
        size: int = 1,
        replace_with: Union[Callable[[Any], Any], Iterable, Any],
        limit: Optional[int] = None,
) -> Iterator:
    """

    >>> data = finite_cycle(3, [0, 1, 2, 5])
    >>> list(replace(data, where=[0, 1, 2], size=3, replace_with=[3, 4]))
    [3, 4, 5, 3, 4, 5, 3, 4, 5]
    >>> items = finite_cycle(5, [0, 1])
    >>> list(replace(items, where=lambda x: x == 1, replace_with=2, limit=2))
    [0, 2, 0, 2, 0, 1, 0, 1, 0, 1]
    >>> word = 'anti-establishment'
    >>> def is_vowel(s): return s.lower() in 'aeiou'
    >>> def to_upper(s): return s.upper()
    >>> ''.join(replace(word, where=is_vowel, replace_with=to_upper))
    'AntI-EstAblIshmEnt'

    """
    if size < 1:
        msg = f'Window size must be at least one item; got {size!r}'
        raise ValueError(msg)
    windows = window(size, pad(iterable, value=_NO_VALUE, times=size - 1))
    replacements = 0
    for values in windows:
        if _to_replace(where, values):
            if limit is None or replacements < limit:
                replacements += 1
                yield from _replace_with(replace_with, values)
                consume(windows, items=size - 1)
                continue
        if values and values[0] is not _NO_VALUE:
            yield values[0]


def _to_replace(where, values):
    if callable(where):
        return where(*values)
    else:
        return tuple(where) == tuple(values)


def _replace_with(replace_with, values):
    if callable(replace_with):
        return replace_with(*values)
    else:
        try:
            return tuple(replace_with)
        except TypeError:
            return (replace_with,)


def tabulate(expr: Callable[[int], Any], *, start: int = 0) -> Iterator:
    """Return an infinite iterator of terms based upon an expression.

    Based upon the expressions, which takes one integer argument, reqturn
    a mathematical or other sequence counting up from the given start point.

    Arguments:
        expression: callable taking one integer argument, returning each term
            of the sequence

    Keyword Arguments:
        start: integral start point of the sequence (optional; default is 0)

    Returns:
        Infinite iterator of sequence terms starting at the start index.

    Examples:

    >>> list(take(5, tabulate(lambda n: n ** 2)))
    [0, 1, 4, 9, 16]
    >>> word = 'supercalifragilistic'
    >>> list(take(5, tabulate(lambda n: word[:n], start=1)))
    ['s', 'su', 'sup', 'supe', 'super']

    """
    return map(expr, itertools.count(start=start))


def difference(
        iterable: Iterable[Any],
        *,
        operation: Callable[[Any, Any], Any] = operator.sub,
) -> Iterator:
    """

    >>> list(difference(range(10)))
    [1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> list(difference([x * x for x in range(10)]))
    [1, 3, 5, 7, 9, 11, 13, 15, 17]
    >>> list(difference(difference([x * x for x in range(10)])))
    [2, 2, 2, 2, 2, 2, 2, 2]
    >>> import itertools
    >>> list(difference(itertools.accumulate(range(10))))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(itertools.accumulate(difference(range(10))))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> words = ['how', 'now', 'brown', 'cow']
    >>> def word_len_diff(s2, s1): return len(s2) - len(s1)
    >>> list(difference(words, operation=word_len_diff))
    [0, 2, -2]
    >>> list(difference([len(word) for word in words]))
    [0, 2, -2]

    """
    return map(lambda x: operation(x[1], x[0]), pairwise(iterable))


def iterate(func: Callable[[Any], Any], *, start: Any) -> Iterator:
    """Return an iterator that iterates a function endlessly.

    Starting with a start value, feed the output value of the function as the
    input value for the next iteration of the function.

    In mathematical notation, if the start value is x and the function is f(x),
    the generator yields:
        x, f(x), f(f(x)), f(f(f(x))), ...

    Arguments:
        func: callable taking a value and returning a value

    Keyword Arguments:
        start: the starting value for the iteration

    Returns:
        Iterator of function values starting with the start value.

    Note:
        * The function should not modify the value of its argument.

    Examples:

    >>> logistic_map = iterate(lambda x: 3.8 * x * (1-x), start=0.4)
    >>> [round(x, 2) for x in take(5, logistic_map)]
    [0.4, 0.91, 0.3, 0.81, 0.6]
    >>> dumb_count = iterate(lambda n: n+1, start=0)
    >>> import itertools
    >>> take(5, dumb_count) == take(5, itertools.count())
    True
    >>> palindrome = 'race car'
    >>> take(4, iterate(lambda s: s[::-1], start=palindrome))
    ['race car', 'rac ecar', 'race car', 'rac ecar']

    """
    x = start
    while True:
        yield x
        x = func(x)


def repeatfunc(
        func: Callable,
        *args,
        times: Optional[int] = None,
        _starmap=itertools.starmap,
        _repeat=itertools.repeat,
) -> Iterator:
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> list(repeatfunc(random.randint, 0, 1000, times=5))
    [137, 582, 867, 821, 782]
    >>> import functools
    >>> randint = functools.partial(random.randint, 0, 1000)
    >>> list(repeatfunc(randint, times=5))
    [64, 261, 120, 507, 779]

    """
    if times is None:
        return _starmap(func, _repeat(args))
    else:
        return _starmap(func, _repeat(args, times))


def keep_calling(
        func: Callable,
        *,
        until_raises: BaseException,
        first: Optional[Callable[[], Any]] = None,
) -> Iterator:
    """Call a function repeatedly until a specified exception is raised.

    This is the same as the function iter_except() from the standard library
    itertools recipes. See some additional useful examples at:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Arguments:
        func: zero-argument callable

    Keyword Arguments:
        until_raises: the exception to be detected to break the infinite loop
        first: optional callable to call before beginning the iteration
            (default is None)

    Yields:
        Result of calling the first() function (if applicable), then the result
        of repeated calls to func().

    Examples:

    >>> s = set('abracadabra')
    >>> sorted(item for item in keep_calling(s.pop, until_raises=KeyError))
    ['a', 'b', 'c', 'd', 'r']
    >>> s
    set()

    """
    try:
        if first is not None:
            yield first()
        while True:
            yield func()
    except until_raises:
        pass


def force_reverse(iterable: Iterable[Any]) -> Iterator:
    try:
        return reversed(iterable)
    except TypeError:
        return reversed(list(iterable))


def most_recent_run(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator:
    """Return an iterator of the unique contiguous items of an iterable.

    Only remember the most recent run of items. THe first item in each
    continguous run will be yielded.

    The optional key callable specifies a transformation of the items
    which is used ot determine whether contiguous items are equal.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None)

    Yields:
        the first item in each contiguous group of the iterable (as transformed
        by the key callable, if applicable), in the order it occurs in the
        iterable

    Note:
        Will not return if passed an infinite iterator.

    Equivalent to unique_justseen() from the itertools recipes.

    >>> list(most_recent_run('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D', 'A', 'B']
    >>> list(most_recent_run('AbBCcAD', key=str.lower))
    ['A', 'b', 'C', 'A', 'D']

    """
    groups = itertools.groupby(iterable, key)
    get_group = operator.itemgetter(1)
    _map = map
    _next = next
    return map(_next, _map(get_group, groups))


def groupby_unsorted(
        sequence: Sequence,
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Tuple[Any, Iterator]]:
    key = key or (lambda x: x)
    indexes = collections.defaultdict(list)
    for index, item in enumerate(sequence):
        indexes[key(item)].append(index)
    for key_value, index_values in indexes.items():
        yield key_value, (sequence[index] for index in index_values)
