import collections
import logging
import reprlib
import weakref

from typing import (
    Hashable,
    Iterable,
    MutableMapping,
    MutableSet,
    Optional,
)

import litecore.mappings.classes
import litecore.sets.mixins

log = logging.getLogger(__name__)


class OrderedSet(
        litecore.sets.mixins.SetMethodsMixin,
        collections.abc.MutableSet,
):
    mapping_factory = collections.OrderedDict

    EQ_ORDER_SENSITIVE = (
        collections.abc.Sequence,
        collections.OrderedDict,
    )

    def __init__(
            self,
            iterable: Iterable[Hashable] = (),
            *,
            ordered_mapping_factory: Optional[MutableMapping] = None,
    ):
        if ordered_mapping_factory is not None:
            self.mapping_factory = ordered_mapping_factory
        self.data = self.mapping_factory.fromkeys(iterable)

    @reprlib.recursive_repr()
    def __repr__(self):
        return f'{type(self).__name__}([' + ', '.join(map(repr, self)) + '])'

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __reversed__(self):
        return reversed(self.data)

    def __contains__(self, value):
        return value in self.data

    def __eq__(self, other):
        if not isinstance(other, collections.abc.Collection):
            return NotImplemented
        elif len(self) != len(other):
            return False
        elif isinstance(other, OrderedSet):
            return list(self) == list(other)
        elif isinstance(other, self.EQ_ORDER_SENSITIVE):
            return list(self) == list(other)
        else:
            return set(self) == set(other)

    def __getstate__(self):
        return (self.data,)

    def __setstate__(self, state):
        self.__init__(state[0])

    def __copy__(self):
        return type(self)(self.data.copy())

    def __deepcopy__(self, memo):
        import copy
        new = type(self)()
        memo[id(self)] = new
        new.data = copy.deepcopy(self.data)
        return new

    def copy(self):
        return self.__copy__()

    def clear(self) -> None:
        self.data.clear()

    def add(self, value: Hashable):
        self.data[value] = None

    def discard(self, value: Hashable):
        self.data.pop(value, None)

    def pop(self, last: bool = True) -> Hashable:
        return self.data.popitem(last)[0]

    def move_to_end(self, key: Hashable, last: bool = True) -> None:
        self.data.move_to_end(key, last)


class LastUpdatedOrderedSet(OrderedSet):
    mapping_factory = litecore.mappings.classes.LastUpdatedOrderedDict


class OrderedWeakSet(weakref.WeakSet):
    set_factory = OrderedSet

    def __init__(
            self,
            iterable: Iterable[Hashable] = (),
            *,
            ordered_set_factory: Optional[MutableSet] = None,
    ):
        super().__init__()
        if ordered_set_factory is not None:
            self.set_factory = ordered_set_factory
        self.data = self.set_factory()
        for item in iterable:
            self.add(item)


class LastUpdatedOrderedWeakSet(OrderedWeakSet):
    set_factory = LastUpdatedOrderedSet
