import collections
import copy
import itertools
import logging

from typing import (
    Any,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Union,
)

log = logging.getLogger(__name__)


class OrderedSet(collections.abc.MutableSet, collections.abc.Sequence):
    def __init__(self, iterable: Optional[Iterable[Hashable]] = None) -> None:
        self._items = end = []
        end += [None, end, end]
        self._map = {}
        if iterable is not None:
            self |= iterable

    def _update(self, items: Iterable):
        if items:
            self._items = list(items)
            self._map = {item: index for index, item in enumerate(items)}
        else:
            self._items = []
            self._map = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._items!r})'

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key: Hashable) -> bool:
        return key in self._map

    def __iter__(self) -> Iterator[Hashable]:
        pass  # TODO: fix this

    def __reversed__(self) -> Iterator[Hashable]:
        return reversed(self._items)

    def __getitem__(
            self,
            index_or_slice: Union[int, slice],
    ) -> Union[Hashable, 'OrderedSet']:  # TODO: fix typing
        items = self._items[index_or_slice]
        if isinstance(items, list):
            return type(self)(items)
        else:
            return items

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, collections.abc.Sequence):
            return list(self) == list(other)
        try:
            other = set(other)
        except TypeError:
            return False
        else:
            return self._map.keys() == other

    def __getstate__(self):
        return (self._items,)

    def __setstate__(self, state):
        self._update(state[0])

    def __copy__(self):
        return type(self)(self._items)

    def __deepcopy__(self):
        return type(self)(copy.deepcopy(self._items))

    def copy(self):
        return self.__copy__()

    def add(self, key: Hashable) -> None:
        if key not in self._map:
            self._map[key] = len(self._items)
            self._items.append(key)

    def discard(self, key: Hashable) -> None:
        if key in self._map:
            index = self._map[key]
            del self._items[index]
            del self._map[key]
            for k, v in self._map.items():
                if v >= index:
                    self._map[k] = v - 1

    def clear(self) -> None:
        self._items.clear()
        self._map.clear()

    def pop(self) -> Hashable:
        item = self._items[-1]
        del self._items[-1]
        del self._map[item]
        return item

    def index(self, key: Hashable) -> int:
        try:
            return self._map[key]
        except KeyError:
            msg = f'{key!r} is not in items'
            raise ValueError(msg)

    def issubset(self, other):
        if len(self) > len(other):
            return False
        return all(item in other for item in self._items)

    def issuperset(self, other):
        if len(self) < len(other):
            return False
        return all(item in self for item in other)

    def union(self, *iterables):
        chain = map(list, itertools.chain([self], iterables))
        items = itertools.chain.from_iterable(chain)
        return type(self)(items)

    def intersection(self, *iterables):
        if iterables:
            common = set.intersection(*map(set, iterables))
            items = (item for item in self._items if item in common)
        else:
            items = self._items
        return type(self)(items)

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, *iterables):
        if iterables:
            other = set.union(*map(set, iterables))
            items = (item for item in self._items if item not in other)
        else:
            items = self._items
        return type(self)(items)

    def symmetric_difference(self, other):
        self_diff = self.difference(other)
        other_diff = type(self)(other).difference(self._items)
        return self_diff.union(other_diff)

    def intersection_update(self, other):
        other = set(other)
        self._update([item for item in self._items if item in other])

    def difference_update(self, *iterables):
        to_remove = set()
        for other in iterables:
            to_remove |= set(other)
        self._update([item for item in self._items if item not in to_remove])

    def symmetric_difference_update(self, other):
        to_add = [item for item in other if item not in self._map]
        to_remove = set(other)
        items = [item for item in self._items if item not in to_remove] + to_add
        self._update(items)


class OrderedSet2(collections.abc.MutableSet, collections.abc.Sequence):
    def __init__(self, iterable: Optional[Iterable[Hashable]] = None) -> None:
        self._update(iterable)

    def _update(self, items: Iterable):
        if items:
            self._items = list(items)
            self._map = {item: index for index, item in enumerate(items)}
        else:
            self._items = []
            self._map = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._items!r})'

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: Hashable) -> bool:
        return key in self._map

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._items)

    def __reversed__(self) -> Iterator[Hashable]:
        return reversed(self._items)

    def __getitem__(
            self,
            index_or_slice: Union[int, slice],
    ) -> Union[Hashable, 'OrderedSet']:  # TODO: fix typing
        items = self._items[index_or_slice]
        if isinstance(items, list):
            return type(self)(items)
        else:
            return items

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, collections.abc.Sequence):
            return list(self) == list(other)
        try:
            other = set(other)
        except TypeError:
            return False
        else:
            return self._map.keys() == other

    def __getstate__(self):
        return (self._items,)

    def __setstate__(self, state):
        self._update(state[0])

    def __copy__(self):
        return type(self)(self._items)

    def __deepcopy__(self):
        return type(self)(copy.deepcopy(self._items))

    def copy(self):
        return self.__copy__()

    def add(self, key: Hashable) -> None:
        if key not in self._map:
            self._map[key] = len(self._items)
            self._items.append(key)

    def discard(self, key: Hashable) -> None:
        if key in self._map:
            index = self._map[key]
            del self._items[index]
            del self._map[key]
            for k, v in self._map.items():
                if v >= index:
                    self._map[k] = v - 1

    def clear(self) -> None:
        self._items.clear()
        self._map.clear()

    def pop(self) -> Hashable:
        item = self._items[-1]
        del self._items[-1]
        del self._map[item]
        return item

    def index(self, key: Hashable) -> int:
        try:
            return self._map[key]
        except KeyError:
            msg = f'{key!r} is not in items'
            raise ValueError(msg)

    def issubset(self, other):
        if len(self) > len(other):
            return False
        return all(item in other for item in self._items)

    def issuperset(self, other):
        if len(self) < len(other):
            return False
        return all(item in self for item in other)

    def union(self, *iterables):
        chain = map(list, itertools.chain([self], iterables))
        items = itertools.chain.from_iterable(chain)
        return type(self)(items)

    def intersection(self, *iterables):
        if iterables:
            common = set.intersection(*map(set, iterables))
            items = (item for item in self._items if item in common)
        else:
            items = self._items
        return type(self)(items)

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, *iterables):
        if iterables:
            other = set.union(*map(set, iterables))
            items = (item for item in self._items if item not in other)
        else:
            items = self._items
        return type(self)(items)

    def symmetric_difference(self, other):
        self_diff = self.difference(other)
        other_diff = type(self)(other).difference(self._items)
        return self_diff.union(other_diff)

    def intersection_update(self, other):
        other = set(other)
        self._update([item for item in self._items if item in other])

    def difference_update(self, *iterables):
        to_remove = set()
        for other in iterables:
            to_remove |= set(other)
        self._update([item for item in self._items if item not in to_remove])

    def symmetric_difference_update(self, other):
        to_add = [item for item in other if item not in self._map]
        to_remove = set(other)
        items = [item for item in self._items if item not in to_remove] + to_add
        self._update(items)
