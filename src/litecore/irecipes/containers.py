import collections
import operator

from typing import (
    Any,
    Callable,
    Container,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

import litecore.utils
from litecore.irecipes.typealiases import KeyFunc

T = TypeVar('T')
HT = TypeVar('HT', int, str, Hashable)
ST = TypeVar('ST', int, str, Hashable)
ItemsCollection = Union[Mapping[ST, T], Sequence[T]]
HashableItemsCollection = Union[Mapping[ST, HT], Sequence[HT]]


def iter_items(iterable: ItemsCollection) -> Iterator[Tuple[ST, T]]:
    """Return iterator of tuples specifying items of a mapping or a sequence.

    The intent is to provide a transparent way to iterate over items of a
    collection that supports subscripting (i.e., mappings or sequences) and
    keep track of the item value as well as the subscript necessary to retrieve
    that item.

    For mappings, returns iterable.items(). For sequences, returns
    enumerate(iterable).

    Arguments:
        iterable: mapping or sequence of items

    Returns:
        iterator of tuples for each item of the iterable, where the second
        component of the tuple is the item and first component of the tuple
        is the subscript that would get the item from the iterable (i.e.,
        item = iterable[subscript])

    Raises:
        TypeError: if passed an iterator or a collection type that does not
            support subscripting (e.g., sets)

    Examples:

    >>> dict_data = {'a': 1, 'b': 2, 'c': 3}
    >>> seq_data = [c for c in 'abc']
    >>> set_data = set(seq_data)
    >>> list(iter_items(dict_data))
    [('a', 1), ('b', 2), ('c', 3)]
    >>> list(iter_items(seq_data))
    [(0, 'a'), (1, 'b'), (2, 'c')]
    >>> list(iter_items(set_data))
    Traceback (most recent call last):
     ...
    TypeError: 'set' object does not support indexing
    >>> list(iter_items(iter(dict_data)))
    Traceback (most recent call last):
     ...
    TypeError: got an iterator, expected a collection

    """
    if litecore.utils.is_iterator(iterable):
        msg = f'got an iterator, expected a collection'
        raise TypeError(msg)
    elif isinstance(iterable, collections.abc.Mapping):
        return iterable.items()
    elif isinstance(iterable, collections.abc.Sequence):
        return enumerate(iterable)
    elif isinstance(iterable, collections.abc.Collection):
        msg = f'{type(iterable).__name__!r} object does not support indexing'
        raise TypeError(msg)
    # fallback to duck-typing
    try:
        return iterable.items()
    except AttributeError:
        pass
    try:
        iterable[0]
    except IndexError:
        return iter(())
    else:
        return enumerate(iterable)


def inverted(iterable: HashableItemsCollection) -> Iterator[Tuple[HT, ST]]:
    return ((v, k) for k, v in iter_items(iterable))


def inverted_last_seen(
        iterable: HashableItemsCollection,
) -> Iterator[Tuple[HT, ST]]:
    seen = dict(inverted(iterable))
    return seen.items()


def inverted_first_seen(
        iterable: HashableItemsCollection,
) -> Iterator[Tuple[HT, ST]]:
    seen = set()
    saw = seen.add
    for v, k in inverted(iterable):
        if v not in seen:
            saw(v)
            yield (v, k)


def inverted_multi_values(
        iterable: HashableItemsCollection,
) -> Iterator[Tuple[HT, HT]]:
    items = iter_items(iterable)
    inverted = collections.defaultdict(list)
    for k, v in items:
        inverted[v].append(k)
    return inverted.items()


def findall(
        items: Container[T],
        iterable: ItemsCollection,
) -> Iterator[Tuple[HT, List[T]]]:
    found = collections.defaultdict(list)
    for subscript, item in iter_items(iterable):
        if item in items:
            found[item].append(subscript)
    return found.items()


def argsort(
    iterable: ItemsCollection,
    *,
    key: Optional[KeyFunc] = None,
    reverse: bool = False,
) -> List[HT]:
    """Return list of indices corresponding to the sorted items of an iterable.

    Similar to numpy.argsort(), except works for general Python mappings and
    sequences. Does not work for sets or other collection types that do not
    support subscripting.

    For mappings, the value of each item will be used for the sort, and the
    returned list will consist of the mapping keys in the order corresponding
    to a sort of values (modified by the key function, if any).

    For sequences, the returned list will consist of the indices from an
    enumeration of the items, in the order corresponding to a sort of the
    values (modifed by the key function, if any).

    Arguments:
        iterable: mapping or sequence of items

    Keyword Arguments:
        key: single-argument callable returning key to be used for sorting
            (optional; default of None means act on items without modification)
        reverse: flag specifying reverse sort order (default is False)

    Returns:
        list of either hashable keys or integer indices corresponding to the
        items of iterable in sorted order

    Raises:
        TypeError: if passed an iterator or a collection type that does not
            support subscripting (e.g., sets)

    Examples:

    >>> items = 'the quick brown fox jumped over the lazy dog'.split()
    >>> argsort(items)
    [2, 8, 3, 4, 7, 5, 1, 0, 6]
    >>> [items[i] for i in argsort(items)] == sorted(items)
    True
    >>> argsort(items, reverse=True) == list(reversed(argsort(items)))
    True
    >>> import operator
    >>> last_char = operator.itemgetter(-1)
    >>> ind_by_last_char = argsort(items, key=last_char)
    >>> ind_by_last_char
    [4, 0, 6, 8, 1, 2, 5, 3, 7]
    >>> [items[i] for i in ind_by_last_char] == sorted(items, key=last_char)
    True
    >>> distinct = 'the quick brown fox jumped over a lazy dog'.split()
    >>> avg_char = lambda s: sum(ord(c) for c in s) / len(s)
    >>> mapping = {s: avg_char(s) for s in distinct}
    >>> argsort(mapping)
    ['a', 'dog', 'the', 'jumped', 'quick', 'brown', 'fox', 'over', 'lazy']
    >>> argsort(mapping) == sorted(distinct, key=avg_char)
    True

    """
    inverse = inverted(iterable)
    if key is None:
        values = sorted(inverse, reverse=reverse)
    else:
        values = sorted(inverse, key=lambda x: key(x[0]), reverse=reverse)
    return [k for v, k in values]


def _argminmax_helper(
    func: Callable,
    index: int,
    iterable: ItemsCollection,
    *,
    key: Optional[Callable[[Any], Any]] = None,
) -> Any:
    if isinstance(iterable, collections.abc.Mapping):
        if key is None:
            return func(iterable.items(), key=operator.itemgetter(1))[0]
        else:
            return func(iterable.items(), key=lambda x: key(x[1]))[0]
    elif isinstance(iterable, collections.abc.Sequence):
        if key is None:
            return iterable.index(func(iterable))
        else:
            return iterable.index(func(iterable, key=key))
    else:
        return argsort(iterable, key=key)[index]


def argmin(
    iterable: ItemsCollection,
    *,
    key: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """Return the index or key of the minimum item in an iterable.

    Arguments:
        iterable: object for which the minimum item is to be determined

    Keyword Arguments:
        key: single-argument callable which will be applied to each item and
            the result of which will be used to determine relative ordering
            of the items (optional; default is None, resulting in the use
            of each item unmodified)

    Returns:
        index of the minimum item in the iterable

    Examples:

    >>> argmin('elephant')
    5
    >>> argmin([[10, 11, 12], [0, 1], [3, 4, 5, 6]], key=len)
    1
    >>> argmin({'a': 1, 'b': 0, 'c': 10})
    'b'
    >>> argmin({'a': 1, 'b': 0, 'c': 10}, key=lambda x: -x)
    'c'
    >>> argmin({'a': 1, 'b': 0, 'c': 10, 'd': 'error'})
    Traceback (most recent call last):
     ...
    TypeError: '<' not supported between instances of 'str' and 'int'

    """
    return _argminmax_helper(min, 0, iterable, key=key)


def argmax(
    iterable: Iterable[Any],
    *,
    key: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """

    Examples:

    >>> argmax('elephant')
    7
    >>> argmax([[10, 11], [0, 1, 2], [3, 4, 5, 6]], key=len)
    2
    >>> argmax({'a': 1, 'b': 0, 'c': 10})
    'c'
    >>> argmax({'a': 1, 'b': 0, 'c': 10}, key=lambda x: -x)
    'b'
    >>> argmax({'a': 1, 'b': 0, 'c': 10, 'd': 'error'})
    Traceback (most recent call last):
     ...
    TypeError: '>' not supported between instances of 'str' and 'int'

    """
    return _argminmax_helper(max, -1, iterable, key=key)


def _allminmax_helper(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
        cmp_func: Callable[[Any], bool],
        equals_func: Callable[[Any], bool] = operator.eq,
) -> Tuple[List[T], List[HT]]:
    items = iter_items(iterable)
    key = key or (lambda x: x)
    results = []
    subscripts = []
    best = None
    for subscript, item in items:
        value = key(item)
        if not results or cmp_func(value, best):
            results = [item]
            subscripts = [subscript]
            best = value
        elif equals_func(value, best):
            results.append(item)
            subscripts.append(subscript)
    return results, subscripts


def allmin(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> List[Any]:
    return _allminmax_helper(iterable, key=key, cmp_func=operator.lt)[0]


def argallmin(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> List[Any]:
    return _allminmax_helper(iterable, key=key, cmp_func=operator.lt)[1]


def argallmin_zipped(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> Iterator[Tuple[HT, T]]:
    results = _allminmax_helper(iterable, key=key, cmp_func=operator.lt)
    return zip(results[1], results[0])


def allmax(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> List[Any]:
    return _allminmax_helper(iterable, key=key, cmp_func=operator.gt)[0]


def argallmax(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> List[Any]:
    return _allminmax_helper(iterable, key=key, cmp_func=operator.gt)[1]


def argallmax_zipped(
        iterable: ItemsCollection,
        *,
        key: Optional[Callable[[Any], Any]] = None,
) -> Iterator[Tuple[HT, T]]:
    results = _allminmax_helper(iterable, key=key, cmp_func=operator.gt)
    return zip(results[1], results[0])
