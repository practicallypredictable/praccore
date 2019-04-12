import collections
import copy
import logging

from typing import (
    Hashable,
    List,
    Optional,
    Tuple,
)

import litecore.mappings.exceptions
import litecore.mappings.abc
import litecore.mappings.mixins

log = logging.getLogger(__name__)


# TODO: checking pickling/json/copy/deepcopy for all

class LastUpdatedOrderedDict(collections.OrderedDict):
    """Store items in the order in which keys were added/updated.

    From the recipe in the Python documentation:
        https://docs.python.org/3/library/collections.html#collections.OrderedDict

    """
    __slots__ = ()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)


class EnhancedDefaultDict(dict):
    def __init__(self, missing=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if missing is not None:
            if callable(missing):
                self._missing = missing
            else:
                self._missing = lambda instance, key: missing
        else:
            self._missing = missing

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._missing!r}, {dict(self)!r})'

    def __missing__(self, key):
        if self._missing is None:
            raise KeyError(key)
        self[key] = value = self._missing(self, key)
        return value

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self._missing, dict(self))

    def __deepcopy__(self, memo):
        return type(self)(self._missing, copy.deepcopy(dict(self)))

    def __reduce__(self):
        return type(self), (self._missing, dict(self))


class EnhancedCounter(collections.Counter):
    def total(self):
        """

        Examples:

        >>> EnhancedCounter('abracadabra').total() == len('abracadabra')
        True

        """
        return sum(self.values())

    def least_common(
            self,
            n: Optional[int] = None,
    ) -> List[Tuple[Hashable, int]]:
        """

        Examples:

        >>> EnhancedCounter('abracadabra').least_common(3)
        [('d', 1), ('c', 1), ('r', 2)]
        >>> EnhancedCounter('abracadabra').least_common()
        [('d', 1), ('c', 1), ('r', 2), ('b', 2), ('a', 5)]

        """
        if n is None:
            return list(reversed(self.most_common()))
        else:
            return self.most_common()[:-(n + 1):-1]


class OrderedCounter(EnhancedCounter, collections.OrderedDict):
    """

    Examples:

    >>> od = OrderedCounter('abracadabra')
    >>> od
    OrderedCounter(OrderedDict([('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]))
    >>> od.least_common()
    [('d', 1), ('c', 1), ('r', 2), ('b', 2), ('a', 5)]

    """

    def __repr__(self) -> str:
        return f'{type(self).__name__}({collections.OrderedDict(self)!r})'

    def __reduce__(self):
        return type(self), (collections.OrderedDict(self),)

# TODO: checking pickling/json/copy/deepcopy for all


@litecore.mappings.abc.implements(dict)
class StringKeyOnlyDict(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(collections.OrderedDict)
class StringKeyOnlyOrderedDict(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(LastUpdatedOrderedDict)
class StringKeyOnlyLastUpdatedOrderedDict(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(collections.defaultdict)
class StringKeyOnlyDefaultDict(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(EnhancedDefaultDict)
class StringKeyOnlyEnhancedDefaultDict(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(collections.Counter)
class StringKeyOnlyCounter(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(EnhancedCounter)
class StringKeyOnlyEnhancedCounter(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass


@litecore.mappings.abc.implements(OrderedCounter)
class StringKeyOnlyOrderedCounter(
        litecore.mappings.mixins.StringKeyOnlyMixin,
        litecore.mappings.abc.BaseMutableMapping,
):
    pass
