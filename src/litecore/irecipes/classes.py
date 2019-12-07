"""Classes implementing the iterator protocol.

"""
import collections.abc

from typing import (
    Any,
    Iterable,
    Tuple,
)

import litecore.irecipes.common as _common

from litecore import LitecoreError as _ErrorBase


class IteratorBoundError(_ErrorBase, RuntimeError):
    """Reached limit of number of items consumed from an iterator."""


class BoundedIterator(collections.abc.Iterator):
    """Iterator which limits maximum number of consumed items.

    Use this as a wrapper around potentially infinite iterators.

    If the keyword argument raise_immediately is False (the default),
    the first attempt to consume an item after hitting the bound will
    raise StopIteration. The next attempt to consume an item will raise
    an IteratorBoundError.

    If raise_immediately is True, an IteratorBoundError will be raised
    as soon as an attempt is made to consume an item after hitting the
    bound.

    If the wrapped iterable is in iterator, it will retain its state
    even after hitting the bound for the wrapping iterator.

    Arguments:
        iterable: iterable object to wrap

    Keyword Arguments:
        bound: positive maximum number of items allowed
        raise_immediately: bool (optional; default is False)

    Raises:
        IteratorBoundError: if an attempt is made to consume more than
            the allowed maximum number of items

    Examples:

    >>> import itertools
    >>> underlying = itertools.count()
    >>> it = BoundedIterator(underlying, bound=5)
    >>> list(it)
    [0, 1, 2, 3, 4]
    >>> it.consumed
    5
    >>> next(it)
    Traceback (most recent call last):
     ...
    classes.IteratorBoundError: hit bound of 5 items consumed
    >>> next(underlying), next(underlying)
    (5, 6)
    >>> it = BoundedIterator(range(8), bound=5, raise_immediately=True)
    >>> it.bound
    5
    >>> it.raise_immediately
    True
    >>> list(it)
    Traceback (most recent call last):
     ...
    classes.IteratorBoundError: hit bound of 5 items consumed

    """
    def __init__(
            self,
            iterable: Iterable[Any],
            *,
            bound: int,
            raise_immediately: bool = False,
    ):
        if bound < 1:
            raise ValueError(f'must allow at least 1 item')
        self._bound = bound
        self._iter = iter(iterable)
        self._raise_immediately = raise_immediately
        self._consumed = 0
        self._hit_bound = False

    @property
    def bound(self) -> int:
        """Inspect the bound for this iterator."""
        return self._bound

    @property
    def raise_immediately(self) -> bool:
        """Inspect what this iterator will do when hitting the bound."""
        return self._raise_immediately

    @property
    def consumed(self) -> int:
        """Return the number of items consumed so far."""
        return self._consumed

    def __iter__(self):
        return self

    def __next__(self):
        if self._consumed < self._bound:
            item = next(self._iter)
            self._consumed += 1
            return item
        else:
            if self._raise_immediately or self._hit_bound:
                msg = f'hit bound of {self._bound} items consumed'
                raise IteratorBoundError(msg)
            else:
                self._hit_bound = True
                raise StopIteration


class CachedIterator(collections.abc.Iterator):
    """Wrapped iterator that allows indexed access backwards and forwards.

    Progressively caches the items of the iterator to allow indexed access.

    The cache is a list of all the visited items, so beware of hanging
    for inifinite iterators and memory usage for a large number of items.

    To 'reset' the cached iterator to point to the start of the items,
    use the method seek() with argument 0.

    Arguments:
        iterable: iterable object to wrap and cache

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
    ('0', '1', '2', '3', '4', '5')
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
    def cache(self) -> Tuple[Any, ...]:
        """Return tuple of items in the cache."""
        return tuple(self._cache)

    def seek(self, index: int):
        """Move the position in the cache to the specified index.

        Position 0 is the beginning of the cache.

        If the position is set beyond the current cache size, additional
        items will be consumed from the iterator and stored in the cache.

        """
        self._index = index
        remainder = index - len(self._cache)
        if remainder > 0:
            _common.consume(self, items=remainder)
