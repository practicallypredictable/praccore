import abc
import collections
import itertools
import logging
import operator
import reprlib

from typing import (
    Any,
    Callable,
    Iterable,
    List,
    NoReturn,
    Optional,
    Sequence,
    Union,
)

from litecore import LitecoreError
import litecore.nested

log = logging.getLogger(__name__)


def recursion_safe_list_equality(one: List[Any], other: List[Any]) -> bool:
    try:
        return one == other
    except RecursionError:
        return litecore.nested.recursive_equality(one, other)


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

    def __init__(self, sequence: Sequence):
        self._sequence = sequence

    def __repr__(self):
        return f'{type(self).__name__}({self._sequence!r})'

    def __str__(self):
        return str(self._sequence)

    def __getitem__(self, index_or_slice: Union[int, slice]):
        return self._sequence[index_or_slice]

    def __len__(self):
        return len(self._sequence)


# TODO: copy/deepcopy


class IndexBoundError(LitecoreError, IndexError):
    """Attempt to increase a BoundedList beyond its length limit."""
    pass


class BoundedList(collections.abc.MutableSequence):
    """

    Examples:

    >>> b = BoundedList(range(5), maxlen=10)
    >>> b
    BoundedList([0, 1, 2, 3, 4])
    >>> b.append('a')
    >>> b.extend('bc')
    >>> len(b)
    8
    >>> b.insert(1, 'd')
    >>> b.insert(-2, 'e')
    >>> len(b)
    10
    >>> b[1]
    'd'
    >>> b[-2]
    'b'
    >>> b[1:3] = 'xy'
    >>> b
    BoundedList([0, 'x', 'y', 2, 3, 4, 'a', 'e', 'b', 'c'])
    >>> b.append('z')
    Traceback (most recent call last):
     ...
    classes.IndexBoundError: already at maximum length 10
    >>> del b[-2]
    >>> del b[1:3]
    >>> b[-3:] = range(3)
    >>> b.sort(reverse=True)
    >>> b
    BoundedList([4, 3, 2, 2, 1, 0, 0])
    >>> b.clear()
    >>> b[:] = range(5)
    >>> b.maxlen
    10
    >>> b.append(b)
    >>> b
    BoundedList([0, 1, 2, 3, 4, ...])
    >>> import pickle
    >>> pickle.loads(pickle.dumps(b)) == b
    True
    >>> import copy
    >>> copy.deepcopy(b) == b
    True

    """

    def __init__(
            self,
            iterable: Iterable[Any] = (),
            *,
            maxlen: int,
    ):
        self.maxlen = maxlen
        self.data = []
        self.extend(iterable)

    @reprlib.recursive_repr()
    def __repr__(self):
        return f'{type(self).__name__}([' + ', '.join(map(repr, self)) + '])'

    def __len__(self):
        return len(self.data)

    @property
    def room(self) -> int:
        return self.maxlen - len(self.data)

    def _raise_at_bound(self) -> NoReturn:
        msg = f'already at maximum length {self.maxlen!r}'
        raise IndexBoundError(msg)

    def _raise_would_exceed_bound(self) -> NoReturn:
        msg = (
            f'adding additional items would exceed '
            f'maximum length {self.maxlen!r}'
        )
        raise IndexBoundError(msg)

    def __getitem__(self, index_or_slice: Union[int, slice]):
        return self.data[index_or_slice]

    def __setitem__(self, index_or_slice: Union[int, slice], value: Any):
        length = len(self.data)
        try:
            start, stop, step = index_or_slice.indices(length)
        except AttributeError:
            self.data[index_or_slice] = value
        else:
            if stop < length:
                self.data[index_or_slice] = value
                return
            if self.room <= 0:
                assert self.room == 0
                self._raise_at_bound()
            if step != 1:
                msg = f'slice step must be 1 to grow bounded list'
                raise ValueError(msg)
            overlap = range(start, stop)
            take = self.room + len(overlap)
            it = iter(value)
            taken = list(itertools.islice(it, take))
            try:
                next(it)
                self._raise_would_exceed_bound()
            except StopIteration:
                self.data[index_or_slice] = taken

    def __delitem__(self, index_or_slice: Union[int, slice]):
        del self.data[index_or_slice]

    def __eq__(self, other):
        if not isinstance(other, collections.abc.Sequence):
            return NotImplemented
        if len(self) != len(other):
            return False
        if isinstance(other, BoundedList):
            other_data = other.data
        else:
            other_data = list(other)
        return recursion_safe_list_equality(self.data, other_data)

    def insert(self, index: int, value: Any, *, suppress_raise: bool = False):
        room = self.room
        if room > 0:
            self.data.insert(index, value)
        else:
            assert room == 0
            if not suppress_raise:
                self._raise_at_bound()

    def append(self, value: Any, *, suppress_raise: bool = False):
        room = self.room
        if room > 0:
            self.data.append(value)
        else:
            assert room == 0
            if not suppress_raise:
                self._raise_at_bound()

    def extend(self, iterable: Iterable[Any], *, suppress_raise: bool = False):
        take = self.room
        if take <= 0:
            assert take == 0
            if not suppress_raise:
                self._raise_at_bound()
        it = iter(iterable)
        self.data.extend(itertools.islice(it, take))
        try:
            next(it)
            if not suppress_raise:
                self._raise_would_exceed_bound()
        except StopIteration:
            pass

    def clear(self):
        self.data.clear()

    def sort(self, key: Optional[Callable] = None, reverse: bool = False) -> None:
        self.data.sort(key=key, reverse=reverse)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.data, maxlen=self.maxlen)

    def __deepcopy__(self, memo):
        import copy
        new = type(self)(maxlen=self.maxlen)
        memo[id(self)] = new
        new.data = copy.deepcopy(self.data, memo)
        return new


class LazyList(collections.abc.MutableSequence):
    def __init__(
            self,
            iterable: Iterable[Any] = (),
            *,
            sequence_factory: Optional[Callable] = None,
    ):
        if sequence_factory is not None:
            self.sequence_factory = sequence_factory
        self._cache = self.sequence_factory()
        self._lazy = iter(iterable)
        self.consumed = False

    @property
    def cache(self) -> List[Any]:
        return SequenceProxyType(self._cache)

    @reprlib.recursive_repr()
    def __repr__(self):
        self._consume_all()
        items = ', '.join(map(repr, self._cache))
        return f'{type(self).__name__}([{items}])'

    def __len__(self):
        self._consume_all()
        return len(self._cache)

    def __iter__(self):
        yield from self._cache
        for value in self._lazy:
            self._cache.append(value)
            yield value

    def __bool__(self):
        if self._cache:
            return True
        try:
            self._consume_next()
        except StopIteration:
            return False
        else:
            return True

    def __eq__(self, other):
        if not isinstance(other, collections.abc.Sequence):
            return NotImplemented
        if len(self) != len(other):
            return False
        if isinstance(other, LazyList):
            other_data = other._cache
        else:
            other_data == list(other)
        return recursion_safe_list_equality(self._cache, other_data)

    def _consume_all(self) -> None:
        self._cache.extend(self._lazy)
        self.consumed = True

    def _consume_next(self) -> None:
        try:
            self._cache.append(next(self._lazy))
        except StopIteration:
            self.consumed = True
            raise

    def _consume_up_to(self, up_to: int) -> None:
        assert up_to >= 0
        self._cache.extend(itertools.islice(
            self._lazy,
            up_to - len(self._cache),
        ))
        try:
            self._consume_next()
        except StopIteration:
            pass

    def _update_cache(self, index_or_slice=None) -> None:
        if self.consumed:
            return
        if index_or_slice is None:
            self._consume_all()
            return
        try:
            index = index_or_slice.stop
        except AttributeError:
            try:
                index = operator.index(index_or_slice)
            except (TypeError, AttributeError, ValueError) as err:
                msg = f'expected an integer or a slice; got {index_or_slice!r}'
                raise TypeError(msg) from err
        if index is None or index < 0:
            self._consume_all()
        else:
            self._consume_up_to(index)

    def _adjust_index(self, index: Optional[int]) -> int:
        if index is not None and index < 0:
            if not self.consumed:
                self._consume_all()
            index = len(self._cache) - abs(index)
            if index < 0:
                raise IndexError('list index out of range')
        return index

    def index(self, value, start=0, stop=None) -> int:
        start = self._adjust_index(start)
        stop = self._adjust_index(stop)
        for i, item in enumerate(itertools.islice(self, start, stop)):
            if item == value:
                return i + start
        raise ValueError(f'{value!r} is not in list')

    def __getitem__(self, index_or_slice):
        self._update_cache(index_or_slice)
        return self._cache[index_or_slice]

    def __setitem__(self, index_or_slice, value):
        self._update_cache(index_or_slice)
        self._cache[index_or_slice] = value

    def __delitem__(self, index_or_slice):
        self._update_cache(index_or_slice)
        del self._cache[index_or_slice]

    def insert(self, index: int, value: Any) -> None:
        if index:
            self._update_cache(index - 1)
        self._cache.insert(index, value)

    def append(self, value: Any) -> None:
        if self.consumed:
            self._cache.append(value)
        else:
            self._lazy = itertools.chain(self._lazy, (value,))

    def extend(self, iterable: Iterable[Any]) -> None:
        if self.consumed:
            self._cache.extend(iterable)
        else:
            self._lazy = itertools.chain(self._lazy, iterable)

    def pop(self, index: int = -1) -> Any:
        if index < 0:
            self._consume_all()
        else:
            self._consume_up_to(index)
        value = self._cache[index]
        del self._cache[index]
        return value

    def remove(self, value) -> None:
        del self[self.index(value)]

    def clear(self) -> None:
        self._cache.clear()
        self._lazy = iter(())
        self.consumed = False

    def sort(self, key=None, reverse=False) -> None:
        self._consume_all()
        self._cache.sort(key=key, reverse=reverse)

    def reverse(self):
        self._consume_all()
        self._cache.reverse()

    def count(self, value) -> int:
        self._consume_all()
        return self._cache.count(value)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        self._consume_all()
        return type(self)(self._cache)

    def __deepcopy__(self, memo):
        import copy
        self._consume_all()
        new = type(self)()
        memo[id(self)] = new
        new.data = copy.deepcopy(self._cache)
        return new


class RecursiveLazyList(LazyList):
    @abc.abstractmethod
    def _producer(self):
        while False:
            yield

    def __init__(self, *args, **kwargs):
        super().__init__(self._producer(*args, **kwargs))


def lazylist(producer):
    return type(RecursiveLazyList)(
        producer.__name__,
        (RecursiveLazyList,),
        dict(_producer=producer),
    )
