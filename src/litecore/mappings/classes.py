import collections
import copy
import functools
import logging

from typing import (
    Callable,
    Hashable,
    Optional,
)

import litecore.validate
from litecore.mappings.types import MutableMappingFactory

log = logging.getLogger(__name__)


# TODO: checking pickling/json/copy/deepcopy for all

class LastUpdatedOrderedDict(collections.OrderedDict):
    """Store items in the order in which keys were added/updated.

    From the recipe in the Python documentation:
        https://docs.python.org/3/library/collections.html#collections.OrderedDict

    """

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)


class OrderedDefaultDict(collections.OrderedDict):
    def __init__(
            self,
            default_factory: Optional[Callable] = None,
            *args,
            **kwargs,
    ):
        if default_factory is not None and not callable(default_factory):
            msg = f'First argument (default_factory) must be callable or None'
            raise TypeError(msg)
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __repr__(self):
        items = list(self.items())
        return f'{type(self).__name__}({self.default_factory!r}, {items!r})'

    def __missing__(self, key: Hashable):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        items = tuple(self.items())
        return type(self)(self.default_factory, copy.deepcopy(items))

    def __reduce__(self):
        args = (self.default_factory,) if self.default_factory else tuple()
        return type(self), args, None, None, iter(self.items())


class OrderedCounter(collections.Counter, collections.OrderedDict):
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


class _RecursiveDefaultDict:
    def __init__(self, factory):
        self._factory = factory

    def __call__(self):
        return self._factory(self)


def recursive_defaultdict(
        defaultdict_factory: MutableMappingFactory = collections.defaultdict,
):
    return defaultdict_factory(_RecursiveDefaultDict(defaultdict_factory))


def nested_defaultdict(
        default_factory,
        *,
        defaultdict_factory: MutableMappingFactory = collections.defaultdict,
        depth: int = 1,
):
    depth = litecore.validate.as_int(depth)
    if depth < 1:
        msg = f'Depth must be >= 1; got {depth!r}'
        raise ValueError(msg)
    factory = functools.partial(defaultdict_factory, default_factory)
    for _ in range(depth - 1):
        factory = functools.partial(defaultdict_factory, factory)
    return factory()
