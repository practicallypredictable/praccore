import collections
import logging

from typing import (
    Any,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Union,
)

import litecore.sets.mixins

log = logging.getLogger(__name__)


class IndexedSet(
        litecore.sets.mixins.SetMethodsMixin,
        collections.abc.MutableSet,
        collections.abc.Sequence,
):
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
        import copy
        return type(self)(copy.deepcopy(self._items))

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
