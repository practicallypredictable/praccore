
import collections
import logging

from typing import (
    Any,
    Iterable,
    Union,
)

import litecore.sequences.sequences

log = logging.getLogger(__name__)


class SequenceProxyType(collections.abc.Sequence):
    """A read-only proxy for generic sequences.

    Arguments:
        sequence: object to proxy

    Examples:

    >>> data = range(5)
    >>> proxy = SequenceProxyType(data)
    >>> proxy
    SequenceProxyType(range(0, 5))
    >>> len(proxy)
    5
    >>> proxy[2]
    2
    >>> proxy[1:-1]
    range(1, 4)
    >>> list(proxy[1:-1])
    [1, 2, 3]
    >>> proxy[2] = None
    Traceback (most recent call last):
     ...
    TypeError: 'SequenceProxyType' object does not support item assignment

    """

    __slots__ = '_sequence'

    def __init__(self, sequence):
        if not isinstance(sequence, collections.abc.Sequence):
            msg = f'{sequence!r} is not a sequence'
            raise TypeError(msg)
        self._sequence = sequence

    def __repr__(self):
        return f'{type(self).__name__}({self._sequence!r})'

    def __getitem__(self, index_or_slice: Union[int, slice]):
        return self._sequence[index_or_slice]

    def __reversed__(self):
        return reversed(self._sequence)

    def __len__(self):
        return len(self._sequence)


class CachedIterator:
    """Wrapped iterator that allows indexed access backwards and forwards.

    Progressively caches the items of the iterator to allow indexed access.

    Note:
        * The cache is a list of all the visited items, so beware of memory
            usage for iterators over large or infinite iterables.
        * If the underlying iterator is infinite, calls to funcitons such as
            len() or constructors such as list() which consume iterators
            will run forever on a CachedIterator unless interrupted.

    To 'reset' the cached iterator to point to the start of the items, use the
    method seek() with argument 0.

    >>> it = CachedIterator((str(n) for n in range(10)))
    >>> next(it), next(it), next(it)
    ('0', '1', '2')
    >>> it.seek(0)
    >>> next(it), next(it), next(it)
    ('0', '1', '2')
    >>> next(it)
    '3'
    >>> it.seek(5)
    >>> next(it)
    '5'
    >>> it.cache
    SequenceProxyType(['0', '1', '2', '3', '4', '5'])
    >>> list(it)
    ['6', '7', '8', '9']
    >>> it.seek(0)
    >>> list(it)
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    >>> it.seek(12)
    >>> next(it)
    Traceback (most recent call last):
     ...
    StopIteration

    """

    __slots__ = ('_iter', '_cache', '_index')

    def __init__(self, iterable: Iterable[Any]):
        self._iter = iter(iterable)
        self._cache = []
        self._index = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._index is not None:
            try:
                item = self._cache[self._index]
            except IndexError:
                self._index = None
            else:
                self._index += 1
                return item
        item = next(self._iter)
        self._cache.append(item)
        return item

    @property
    def cache(self):
        """Return proxy of items in the cache."""
        return SequenceProxyType(self._cache)

    def seek(self, index: int):
        """Move the position in the cache to specified index.

        If the position is set beyond the current cache size, additional items
        will be consumed from the iterator and stored in the cache.

        """
        self._index = index
        remainder = index - len(self._cache)
        if remainder > 0:
            litecore.sequences.sequences.consume(self, items=remainder)
