
import collections
import functools
import itertools
import logging
import operator

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from litecore.sentinels import NO_VALUE

log = logging.getLogger(__name__)

DO_NOT_FLATTEN = (str, bytes, bytearray)
"""Native data types which should not be flattened or recursed into."""


def iter_with(iterable: Iterable[Any]) -> Iterator[Any]:
    with iterable:
        for item in iterable:
            yield item


def consume(iterator: Iterator[Any], *, items: Optional[int] = None) -> None:
    """Consume items of an iterator.

    Without the optional items keyword argument, consumes all of the iterator
    quickly. With items specified, consumes at most that many items of the
    iterator. If the iterator has fewer items than the specified number, the
    iterator will be fully consumed.

    Arguments:
        iterator: object to be acted upon

    Keyword Arguments:
        items: number of items to consume (optional; default is None)

    Note:
        Will not return if passed an infinite iterator.

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


def first(
    iterable: Iterable[Any],
    *,
    key: Optional[Callable[[Any], bool]] = None,
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
        iterable: the object with items to be tested

    Keyword Arguments:
        key: callable defining condition to be tested
            (optional; default is None)
        default: value to return if the passed iterable is empty, or there is
            no item for which the condition is True
            (optional; default is None)

    Returns:
        First item of the passed iterable, or, if the iterable is empty or no
        item matches the condition, the default value

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
    items = filter(key, iterable) if key is not None else iterable
    return next(iter(items), default)


def skip_first(iterable: Iterable[Any]) -> Iterator[Any]:
    """Return iterator over all the items of an iterable except the first.

    If the iterable is an iterator, it will be fully consumed.

    Arguments:
        iterable: object to be iterated over

    Returns:
        Iterator of all items in iterable, skipping the first.

    Examples:

    >>> list(skip_first(range(1, 5)))
    [2, 3, 4]

    """
    return itertools.islice(iterable, 1, None)


def take(items: int, iterable: Iterable[Any]) -> List[Any]:
    """Return a list of the first specified number of items of an iterable.

    If the passed iterable has length less than or equal to the specified
    number of items, a list having all the items of the iterable will be
    returned.

    If the iterable is an iterator, the specified number of items of the
    iterator will be consumed.

    Arguments:
        items: non-negative number of items to be processed
        iterable: object to be acted upon

    Returns:
        List of length min(len(iterable), items)

    Credit to:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Examples:

    >>> take(1, range(5))
    [0]
    >>> take(2, range(5))
    [0, 1]
    >>> take(0, range(5))
    []
    >>> take(6, iter(range(5)))
    [0, 1, 2, 3, 4]

    """
    return list(itertools.islice(iterable, items))


def take_batches(items: int, iterable: Iterable[Any]) -> Iterator[List[Any]]:
    """

    >>> list(take_batches(3, range(8)))
    [[0, 1, 2], [3, 4, 5], [6, 7]]
    >>> list(take_batches(10, iter(range(8))))
    [[0, 1, 2, 3, 4, 5, 6, 7]]
    >>> list(take_batches(3, []))
    []

    """
    return iter(functools.partial(take, items, iter(iterable)), [])


def take_indices(
    indices: Sequence[int],
    iterable: Iterable[Any],
) -> Iterator[Any]:
    """

    >>> data = range(10)
    >>> it = iter(data)
    >>> take_indices([1, 3, 5], data)
    [1, 3, 5]
    >>> take_indices([1, 3, 5], it)
    [1, 3, 5]
    >>> list(it)
    [6, 7, 8, 9]
    >>> take_indices([1, 11], data)
    Traceback (most recent call last):
     ...
    IndexError: range object index out of range


    """
    try:
        return [iterable[item] for item in indices]
    except TypeError:
        items = take(max(indices) + 1, iterable)
        return [items[item] for item in indices]


def groups_of(
        items: int,
        iterable: Iterable[Any],
        *,
        fillvalue: Optional[Any] = None,
) -> Iterator[Tuple[Any, ...]]:
    """

    >>> list(groups_of(3, 'ABCDEFG', fillvalue=None))
    [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', None, None)]

    """
    groups = [iter(iterable)] * items
    return itertools.zip_longest(*groups, fillvalue=fillvalue)


def only_one(
        iterable: Iterable[Any],
        *,
        raise_empty: Optional[BaseException] = None,
        raise_too_long: Optional[BaseException] = None,
) -> Any:
    iterator = iter(iterable)
    try:
        value = next(iterator)
    except StopIteration:
        raise raise_empty or ValueError(f'Empty iterable')
    try:
        next(iterator)
    except StopIteration:
        # This is the desired outcome
        pass
    else:
        raise raise_too_long or ValueError(f'More than one item in iterable')
    return value


def nth(
    item: int,
    iterable: Iterable[Any],
    *,
    key: Optional[Callable[[Any], bool]] = None,
    default: Optional[Any] = None,
) -> Any:
    """Return n-th item of an iterable for which a condition is true.

    The default condition is to just return the n-th item in the iterable
    (i.e., the implicit condition is that the item exists). Pass the bool
    constructor if you just want to return the n-th "truthy" value.

    If the iterable is empty, or no value is found matching the desired
    condition, return the default value.

    If the iterable is an iterator, its items up to and including the n-th to
    test True will be consumed.

    Arguments:
        iterable: object to act upon

    Keyword Arguments:
        key: callable defining condition to be tested
            (optional; default is None)
        default: value to return if the passed iterable is empty, or there is
            no item for which the condition is True
            (optional; default is None)

    Returns:
        Specified item number of the passed iterable, or, if the iterable is
        empty or no item matches the condition, the default value

    Note:
        Item counting starts with 0, as is usual for Python indexing.

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
    items = filter(key, iterable) if key is not None else iterable
    try:
        # this will be fast for sequences
        return items[item]
    except IndexError:
        # it's an empty sequence
        return default
    except TypeError:
        # it's not a sequence
        return next(itertools.islice(items, item, None), default)


def tail(items: int, iterable: Iterable[Any]) -> Iterator[Any]:
    """Return iterator over the last specified number of items of iterable.

    If the number of items exceeds the length of the iterable, every item
    of the iterable will be contained in the resulting iterator.

    If the given iterable is an iterator, it will be fully consumed.

    Arguments:
        items: non-negative number of items to be returned as output
        iterable: object to be acted upon

    Returns:
        Iterator of the last items in the iterable.

    Note:
        * Will not return if passed an infinite iterator.

    Examples;

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
        return iterable[-items:]
    except TypeError:
        return iter(collections.deque(iterable, maxlen=items))


def last(iterable: Iterable[Any], *, default: Optional[Any] = None) -> Any:
    """Return the last item of an iterable.

    If the iterable is empty, return the default value.

    If the given iterable is an iterator, it will be fully consumed.

    Arguments:
        iterable: object to be acted upon

    Keyword Arguments:
        default: value to return if the iterable is emtpy
            (optional; defaults to None)

    Returns:
        Last item in the iterable, or the default value if the iterator is
        empty.

    Note:
        Will not return if passed an infinite iterator.

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


def butlast(iterable: Iterable[Any]) -> Iterator[Any]:
    """

    Examples:

    >>> list(butlast(range(5)))
    [0, 1, 2, 3]
    >>> list(butlast(iter(range(5))))
    [0, 1, 2, 3]

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
        key: Optional[Callable[[Any], Any]] = None,
) -> Iterator[Tuple[int, Any]]:
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
        key: Optional[Callable[[Any], Any]] = None,
) -> Iterator[Any]:
    """Return iterator of unique items in an iterable object.

    The optional key is a callable that, if provided, will be called on each
    item prior to determining uniqueness. Only items with different keys
    will compare as different. The default is None, which simply operates
    on each item directly.

    The items in the iterable may be hashable or unhashable.

    Arguments:
        iterable: object to be acted upon

    Keyword Arguments:
        key: callable mapping function (optional; defaults to None)

    Returns:
        Iterator of unique values in the order they were encountered

    Note:
        Will not return if passed an infinite iterator.

    >>> list(unique('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D']
    >>> list(unique('ABBCcAD', key=str.lower))
    ['A', 'B', 'C', 'D']
    >>> list(unique([]))
    []
    >>> list(unique(range(10), key=type))
    [0]
    >>> unhashable = [{'value': n, 'even': n % 2 == 0} for n in range(1, 10)]
    >>> import operator
    >>> list(unique(unhashable, key=operator.itemgetter('even')))
    [{'value': 1, 'even': False}, {'value': 2, 'even': True}]

    """
    for i, item in unique_with_index(iterable, key=key):
        yield item


def argunique(iterable, *, key=None) -> Iterator[int]:
    """

    >>> list(argunique('AAAABBBCCDAABBB'))
    [0, 4, 7, 9]
    >>> list(argunique('ABBCcAD', key=str.lower))
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
    for i, item in unique_with_index(iterable, key=key):
        yield i


def drop(items: int, iterable: Iterable[Any]) -> Iterator[Any]:
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


def flatten(iterables: Iterable[Iterable[Any]]) -> Iterator[Any]:
    """Flatten an iterable of iterables into one consecutive iterator.

    Does not recurse into deeper-level iterables.

    Arguments:
        iterables: iterable of iterables

    Returns:
        Iterator of the consecutive items of the underlying iterables.

    Examples:

    >>> list(flatten([range(3), [-1], range(3, 6)]))
    [0, 1, 2, -1, 3, 4, 5]
    >>> ' '.join(flatten(['abc', 'def', 'ghi', 'jkl']))
    'a b c d e f g h i j k l'

    """
    return itertools.chain.from_iterable(iterables)


def flatten_recursive(
        iterable: Iterable[Any],
        *,
        ignore_types: Optional[Sequence[Type]] = None,
        levels: Optional[int] = None,
) -> Iterator[Any]:
    """Recursively flatten an iterable of items into one iterator.

    To avoid hitting the recursion depth limit, ignore_types will always be
    treated to include str and bytes. These will implicitly be added to
    whatever sequence is provided by the caller (including None). See the
    Examples.

    Arguments:
        items: iterable of items to be flattened

    Keyword Arguments:
        ignore_types: sequence of types which will not be recursed into;
            implicitly includes str and bytes, which is also the default

    Returns:
        Iterator of the consecutive items of the underlying iterables.

    Examples:

    >>> list(flatten_recursive([range(3), [-1], range(3, 6)]))
    [0, 1, 2, -1, 3, 4, 5]
    >>> ' '.join(flatten_recursive(['abc', 'def']))
    'abc def'
    >>> ' '.join(flatten_recursive(['abc', 'def'], ignore_types=None))
    'abc def'
    >>> items = [1, [2, (3, 4, {5: 6}, 7), 8], 9]
    >>> list(flatten_recursive(items))
    [1, 2, 3, 4, 5, 7, 8, 9]
    >>> list(flatten_recursive(items, ignore_types=(tuple, dict)))
    [1, 2, (3, 4, {5: 6}, 7), 8, 9]
    >>> names = ['alice', ['bob', ('charlie', 'david', {'edward': 'fiona'})]]
    >>> list(flatten_recursive(names))
    ['alice', 'bob', 'charlie', 'david', 'edward']
    >>> list(flatten_recursive(names, ignore_types=(tuple, dict)))
    ['alice', 'bob', ('charlie', 'david', {'edward': 'fiona'})]

    """
    def walk(node, level):
        stop_level = (levels is not None and level > levels)
        ignore_type = (
            (ignore_types is not None and isinstance(node, ignore_types))
            or isinstance(node, DO_NOT_FLATTEN)  # noqa: W503
        )
        if stop_level or ignore_type:
            yield node
            return
        try:
            children = iter(node)
        except TypeError:
            yield node
            return
        else:
            for child in children:
                for item in walk(child, level + 1):
                    yield item

    yield from walk(iterable, 0)


def flatmap(
        func: Callable[[Any], Any],
        iterable: Iterable[Any],
) -> Iterator[Any]:
    return itertools.chain.from_iterable(map(func, iterable))


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
        Tuple of the first item and an iterator equivalent to the original

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
) -> Iterator[Any]:
    """Return an iterator with a specified value prepended.

    Arguments:
        value: the value to prepend to the iterable
        iterable: the iterable to which the value is to be prepended

    Keyword Arguments:
        times: number of times to prepend the value (optional; default is 1)

    Returns:
        Iterable combining the prepended value and the original iterable

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
) -> Iterator[Any]:
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


def finite_cycle(times: int, iterable: Iterable[Any]) -> Iterator[Any]:
    """Return iterator cycling through a given iterable finitely-many times.

    The passed iterable is assumed to be finite.

    Arguments:
        times: integral number of times to repeat the iterable
        iterable: finite iterable to be repeated

    Returns:
        Iterator repeating the passed iterable the specified number of times.

    Notes:
        * Will not return if passed an infinite iterator.

    Examples:

    >>> pattern = 'hee haw'.split()
    >>> list(finite_cycle(3, pattern))
    ['hee', 'haw', 'hee', 'haw', 'hee', 'haw']

    """
    return itertools.chain.from_iterable(itertools.repeat(tuple(iterable), times))


def enumerate_cycle(iterable, *, times: Optional[int] = None):
    iterable = tuple(iterable)
    if not iterable:
        return iter(())
    counter = itertools.count() if times is None else range(times)
    return ((i, item) for i in counter for item in iterable)


def round_robin(*iterables: Tuple[Iterable[Any]]) -> Iterator[Any]:
    """Return iterator yielding from each iterable in turn.

    Stop when the last item from the shortest iterable is yielded.

    Arguments:
        Arbitrary number of iterable positional arguments

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


def round_robin_longest(*iterables: Iterable[Any]) -> Iterator[Any]:
    """Return iterator yielding from each iterable in turn.

    Continue until all iterables have been consumed. As each iterable is
    consumed, it falls out of the rotation.

    Arguments:
        Arbitrary number of iterable positional arguments

    Returns:
        Iterator rotating among iterable arguments until all are exhausted.

    Examples:

    >>> numbers = range(3)
    >>> chars = 'abcde'
    >>> classes = [int, str, dict, list]
    >>> list(round_robin_longest(numbers, chars, classes))  # doctest: +ELLIPSIS
    [0, 'a', ... 2, 'c', <class 'dict'>, 'd', <class 'list'>, 'e']

    """
    zipped = itertools.zip_longest(*iterables, fillvalue=NO_VALUE)
    chained = itertools.chain.from_iterable(zipped)
    return itertools.filterfalse(lambda item: item == NO_VALUE, chained)


def rotate_cycle(iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
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
) -> Iterator[Any]:
    """Introduce a value between items of an iterable.

    The default behavior is to introduce the value between every item of the
    iterable. This can be altered by providing the spacing keyword argument.

    The iterator's last item will be the last item of the original iterable.

    Arguments:
        value: the value to introduce
        iterable: the object containing the items to be iterated

    Keyword Arguments:
        spacing: integer number of items from the original iterable to take
            before introducing the value (optional; default is 1)

    Returns:
        Iterator with the value introduced between the items of the original
            iterable.

    Note:
        * Will not return if passed an infinite iterator.

    >>> list(intersperse('hiya', range(5)))
    [0, 'hiya', 1, 'hiya', 2, 'hiya', 3, 'hiya', 4]
    >>> list(intersperse('hiya', range(5), spacing=2))
    [0, 1, 'hiya', 2, 3, 'hiya', 4]
    >>> list(intersperse('hiya', range(4), spacing=2))
    [0, 1, 'hiya', 2, 3]

    """
    if spacing <= 0:
        msg = f'Got spacing argument {spacing!r}; must be positive'
        raise ValueError(msg)
    elif spacing == 1:
        filler = itertools.repeat(value)
        return skip_first(round_robin(filler, iterable))
    else:
        filler = itertools.repeat([value])
        batches = take_batches(spacing, iterable)
        return flatten(skip_first(round_robin(filler, batches)))


def partition(
        iterable: Iterable[Any],
        *,
        by: Callable[[Any], bool],
) -> Tuple[Iterator[Any], Iterator[Any]]:
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


def split(iterable, *, at: int):
    first, second = itertools.tee(iterable)
    return itertools.islice(first, at), itertools.islice(second, at, None)


def take_then_split(iterable, *, until: Callable):
    first, second = itertools.tee(iterable)
    return itertools.takewhile(until, first), itertools.dropwhile(until, second)


def split_after(iterable, *, each_time: Callable):
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
        fillvalue: Optional[Any] = None,
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
        item, iterator = peek(iterator, default=NO_VALUE)
        if item is NO_VALUE:
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


def pairwise(iterable: Iterable[Any]) -> Iterator[Any]:
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
        where: Union[Callable[[Any], bool], Iterable[Any], Any],
        size: int = 1,
        replace_with: Union[Callable[[Any], Any], Iterable[Any], Any],
        limit: Optional[int] = None,
) -> Iterator[Any]:
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
    windows = window(size, pad(iterable, value=NO_VALUE, times=size - 1))
    replacements = 0
    for values in windows:
        if _to_replace(where, values):
            if limit is None or replacements < limit:
                replacements += 1
                yield from _replace_with(replace_with, values)
                consume(windows, items=size - 1)
                continue
        if values and values[0] is not NO_VALUE:
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


def tabulate(expr: Callable[[int], Any], *, start: int = 0) -> Iterator[Any]:
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
) -> Iterator[Any]:
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


def iterate(func: Callable[[Any], Any], *, start: Any) -> Iterator[Any]:
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


def repeat_calling(
        func: Callable,
        *args,
        times: Optional[int] = None,
):
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> import functools
    >>> randint = functools.partial(random.randint, 0, 1000)
    >>> list(repeat_calling(randint, times=5))
    [137, 582, 867, 821, 782]

    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    else:
        return itertools.starmap(func, itertools.repeat(args, times))


def keep_calling(
        func: Callable,
        *,
        until_raises: BaseException,
        first: Optional[Callable[[], Any]] = None,
) -> Iterator[Any]:
    """Call a function repeatedly until a specified exception is raised.

    This is the same as the function iter_except() from the standard library
    itertools recipes. See some additional useful examples at:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Arguments:
        func: callable that takes no arguments

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


def force_reverse(iterable: Iterable[Any]) -> Iterator[Any]:
    try:
        return reversed(iterable)
    except TypeError:
        return reversed(list(iterable))


def zip_strict(
        *iterables: Tuple[Iterable[Any], ...],
) -> Iterator[Tuple[Any, ...]]:
    """Same as built-in zip(), except requires all iterable to be equal-length.

    Arguments:
        Arbitrary number of iterable positional arguments

    Yields:
        Iterator of zipped tuples of the arguments

    Raises:
        ValueError: if the iterables are not equal-length

    Credit to:
        https://treyhunner.com/2019/03/unique-and-sentinel-values-in-python/

    Examples:

    >>> list(zip_strict('abcd', range(4)))
    [('a', 0), ('b', 1), ('c', 2), ('d', 3)]
    >>> list(zip_strict('abcd', range(5)))
    Traceback (most recent call last):
     ...
    ValueError: All iterables must have the same length
    >>> list(zip_strict('', []))
    []

    """
    for values in itertools.zip_longest(*iterables, fillvalue=NO_VALUE):
        if any(v is NO_VALUE for v in values):
            msg = f'All iterables must have the same length'
            raise ValueError(msg)
        yield values


def unzip(iterable):
    """

    >>> letters, numbers = unzip(zip('abcd', range(8)))
    >>> tuple(letters)
    ('a', 'b', 'c', 'd')
    >>> tuple(numbers)
    (0, 1, 2, 3)
    >>> import itertools
    >>> inf_letters = itertools.cycle('abcd')
    >>> inf_numbers = itertools.count()
    >>> letters, numbers = unzip(zip(inf_letters, inf_numbers))
    >>> take(6, letters)
    ['a', 'b', 'c', 'd', 'a', 'b']
    >>> take(8, numbers)
    [0, 1, 2, 3, 4, 5, 6, 7]
    >>> list(unzip(zip('abcd', [])))
    []
    >>> new_letters, new_numbers = unzip(zip('abcd', range(3)))
    >>> list(new_letters)
    ['a', 'b', 'c']
    >>> list(new_numbers)
    [0, 1, 2]

    """
    first, iterator = peek(iter(iterable))
    if first is None:
        return ()
    tees = itertools.tee(iterator, len(first))
    return (map(operator.itemgetter(i), t) for i, t in enumerate(tees))


def unzip_finite(iterable):
    """

    >>> letters, numbers = unzip_finite(zip('abcd', range(8)))
    >>> letters
    ('a', 'b', 'c', 'd')
    >>> numbers
    (0, 1, 2, 3)
    >>> list(unzip_finite(zip('abcd', [])))
    []
    >>> new_letters, new_numbers = unzip(zip('abcd', range(3)))
    >>> list(new_letters)
    ['a', 'b', 'c']
    >>> list(new_numbers)
    [0, 1, 2]

    """
    for z in zip(*iterable):
        yield z


def unzip_longest_finite(iterable, *, fillvalue: Optional[Any] = None):
    """

    >>> import itertools
    >>> zipped = itertools.zip_longest('abcd', range(8))
    >>> letters, numbers = unzip_longest_finite(zipped)
    >>> letters
    ('a', 'b', 'c', 'd')
    >>> numbers
    (0, 1, 2, 3, 4, 5, 6, 7)
    >>> list(unzip_longest_finite(zip('abcd', [0])))
    [('a',), (0,)]

    """
    for z in zip(*iterable):
        yield tuple(x for x in z if x != fillvalue)


def most_recent_run(
        iterable: Iterable[Any],
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> Iterator[Any]:
    """

    >>> list(most_recent_run('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D', 'A', 'B']
    >>> list(most_recent_run('AbBCcAD', key=str.lower))
    ['A', 'b', 'C', 'A', 'D']

    """
    groups = itertools.groupby(iterable, key)
    return map(next, map(operator.itemgetter(1), groups))


def groupby_unsorted(
        sequence: Sequence,
        *,
        key: Callable[[Any], Any] = lambda x: x,
) -> Iterator[Tuple[Any, Iterator[Any]]]:
    indexes = collections.defaultdict(list)
    for index, item in enumerate(sequence):
        indexes[key(item)].append(index)
    for key, index_values in indexes.items():
        yield key, (sequence[index] for index in index_values)


def argsort(
    iterable: Iterable[Any],
    *,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> Sequence[Any]:
    if isinstance(iterable, collections.abc.Mapping):
        iterator = ((v, k) for k, v in iterable.items())
    else:
        iterator = ((v, k) for k, v in enumerate(iterable))
    if key is None:
        indices = [k for v, k in sorted(iterator, reverse=reverse)]
    else:
        indices = [k for v, k in sorted(
            iterator, key=lambda item: item[0], reverse=reverse)]
    return indices
