import abc
import collections
import itertools
import logging

from typing import (
    Iterable,
)

log = logging.getLogger(__name__)

_FAST_LOOKUP_TYPES = (
    collections.abc.Set,
    collections.abc.Mapping,
)


class SetMethodsMixin(abc.ABC):
    def _overwrite(self, iterable: Iterable):
        self.clear()
        for item in iterable:
            self.add(item)

    @abc.abstractmethod
    def copy(self):
        pass

    def issubset(self, other):
        if not isinstance(other, collections.abc.Set):
            return NotImplemented
        if len(self) > len(other):
            return False
        return all(item in other for item in self)

    def issuperset(self, other):
        if not isinstance(other, collections.abc.Set):
            return NotImplemented
        if len(self) < len(other):
            return False
        return all(item in self for item in other)

    __le__ = issubset

    __ge__ = issuperset

    def union(self, *iterables):
        chain = map(list, itertools.chain([self], iterables))
        items = itertools.chain.from_iterable(chain)
        return type(self)(items)

    def intersection(self, *iterables):
        if iterables:
            common = set.intersection(*map(set, iterables))
            return type(self)(item for item in self if item in common)
        else:
            return self.copy()

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, *iterables):
        if iterables:
            unions = set.union(*map(set, iterables))
            return type(self)(item for item in self if item not in unions)
        else:
            return self.copy()

    def symmetric_difference(self, other):
        self_diff = self.difference(other)
        other_diff = type(self)(other).difference(self)
        return self_diff.union(other_diff)

    def intersection_update(self, other):
        if not isinstance(other, _FAST_LOOKUP_TYPES):
            other = set(other)
        items = list(item for item in self if item in other)
        self._overwrite(items)

    def difference_update(self, *iterables):
        to_remove = set()
        for other in iterables:
            if not isinstance(other, _FAST_LOOKUP_TYPES):
                to_remove |= set(other)
            else:
                to_remove |= other
        items = list(item for item in self if item not in to_remove)
        self._overwrite(items)

    def symmetric_difference_update(self, other):
        if not isinstance(other, _FAST_LOOKUP_TYPES):
            other = set(other)
        to_add = (item for item in other if item not in self)
        to_keep = (item for item in self if item not in other)
        # TODO: optimization?
        items = list(itertools.chain(to_keep, to_add))
        self._overwrite(items)
