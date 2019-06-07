import bisect
import collections
import itertools
import operator

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Tuple,
    Union,
)


class SortedList(collections.abc.MutableSequence):
    @staticmethod
    def default_key(x: Any) -> Any:
        return x

    def __init__(
            self,
            iterable: Iterable[Any] = (),
            *,
            key: Callable = None,
    ) -> None:
        self._keys = []
        self._values = []
        self._key_arg = key
        if key is None:
            key = self.default_key
        self._update(iterable, key=key)

    def _update(self, iterable: Iterable[Any], *, key: Callable) -> None:
        if iterable:
            keyed = sorted(
                ((key(item), i, item) for i, item in enumerate(iterable)),
                key=operator.itemgetter(0),
            )
            self._keys = [k for k, i, v in keyed]
            self._values = [v for k, i, v in keyed]
        else:
            self._keys.clear()
            self._values.clear()
        self._key_used = key

    @property
    def key(self) -> Callable:
        return self._key_used

    @key.setter
    def key(self, key) -> None:
        if key is not self._key_used:
            items = (item.value for item in self._values)
            self._update(items, key=key)

    @key.deleter
    def key(self) -> None:
        self.key = None

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._values!r}, key={self.key!r})'

    def _bracket(self, item: Any) -> Tuple[int, int]:
        key = self.key(item)
        left = bisect.bisect_left(self._keys, key)
        right = bisect.bisect_right(self._keys, key)
        return left, right

    def __contains__(self, item: Any) -> bool:
        left, right = self._bracket(item)
        return item in self._values[left:right]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def __reversed__(self) -> List[Any]:
        return reversed(self._values)

    def __eq__(self, other):
        if isinstance(other, SortedList):
            if len(self) != len(other):
                return False
            return self._values == other._values
        elif isinstance(other, collections.abc.Sequence):
            if len(self) != len(other):
                return False
            return self._values == other
        else:
            return NotImplemented

    def __getitem__(self, index_or_slice: Union[int, slice]):
        if isinstance(index_or_slice, slice):
            extract = type(self)(key=self.key)
            extract._keys = self._keys[index_or_slice]
            extract._values = self._values[index_or_slice]
            return extract
        else:
            return self._values[index_or_slice]

    def __setitem__(self, index_or_slice, value: Any) -> None:
        msg = f'use del to remove item(s), then insert() or insert_right()'
        raise NotImplementedError(msg)

    def __add__(self, other):
        if isinstance(other, SortedList):
            values = self._values
            values.extend(other._values)
        elif isinstance(other, collections.abc.Sequence):
            values = self._values
            values.extend(other)
        else:
            return NotImplemented
        return type(self)(values, key=self.key)

    __radd__ = __add__

    def __iadd__(self, other):
        self.extend(other)
        return self

    def _mul_values(self, n: int) -> Iterator[Any]:
        repeated = (itertools.repeat(item, n) for item in self._values)
        return itertools.chain.from_iterable(repeated)

    def __mul__(self, n: int):
        return type(self)(self._mul_values(n), key=self.key)

    __rmul__ = __mul__

    def __imul__(self, n: int):
        values = list(self._mul_values(n))
        self.clear()
        self._update(values, key=self.key)
        return self

    def __delitem__(self, index_or_slice: Union[int, slice]) -> None:
        # TODO: transaction logic
        del self._keys[index_or_slice]
        del self._values[index_or_slice]

    def __getnewargs_ex__(self):
        args = (iter(self._values),)
        kwargs = {'key': self.key}
        return (args, kwargs)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self._values, key=self.key)

    def index(self, item: Any) -> int:
        left, right = self._bracket(item)
        return self._values.index(item, left, right)

    def find(self, key):
        left = bisect.bisect_left(self._keys, key)
        if left != len(self) and self._keys[left] == key:
            return self._values[left]
        msg = f'no item found with key {key!r}'
        raise ValueError(msg)

    def count(self, item: Any) -> int:
        left, right = self._bracket(item)
        return self._values[left:right].count(item)

    def remove(self, item) -> None:
        i = self.index(item)
        del self._keys[i]
        del self._values[i]

    def clear(self) -> None:
        self._update((), key=self.key)

    def insert(self, item: Any) -> None:
        key = self.key(item)
        left = bisect.bisect_left(self._keys, key)
        self._keys.insert(left, key)
        self._values.insert(left, item)

    def insert_right(self, item: Any) -> None:
        key = self.key(item)
        right = bisect.bisect_right(self._keys, key)
        self._keys.insert(right, key)
        self._values.insert(right, item)

    def append(self, item: Any) -> None:
        msg = f'use insert() or insert_right()'
        raise NotImplementedError(msg)

    def extend(self, iterable: Iterable[Any]) -> None:
        items = sorted(iterable, key=self.key)
        for item in items:
            self.insert_right(item)

    def index_lt(self, key):
        left = bisect.bisect_left(self._keys, key)
        if left:
            return left - 1
        msg = f'no item found with key < {key!r}'
        raise ValueError(msg)

    def index_le(self, key):
        right = bisect.bisect_right(self._keys, key)
        if right:
            return right - 1
        msg = f'no item found with key <= {key!r}'
        raise ValueError(msg)

    def index_gt(self, key):
        right = bisect.bisect_right(self._keys, key)
        if right != len(self):
            return right
        msg = f'no item found with key >= {key!r}'
        raise ValueError(msg)

    def index_ge(self, key):
        left = bisect.bisect_left(self._keys, key)
        if left != len(self):
            return left
        msg = f'no item found with key > {key!r}'
        raise ValueError(msg)

    def find_lt(self, key):
        return self._values[self.index_lt(key)]

    def find_le(self, key):
        return self._values[self.index_le(key)]

    def find_gt(self, key):
        return self._values[self.index_gt(key)]

    def find_ge(self, key):
        return self._values[self.index_ge(key)]
