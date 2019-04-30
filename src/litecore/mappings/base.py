import collections
import copy
import logging
import types

from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    TypeVar,
    Union,
)

from litecore.mappings.types import MappingFactory, MutableMappingFactory
import litecore.mappings.classes

log = logging.getLogger(__name__)

# TODO: checking pickling/json/copy/deepcopy for all concrete (__slots__!)
# TODO: dict vs factory in pickling/copy?
# TODO: performance optimiozatinos for all abc methods

_MF = TypeVar('_MF', MappingFactory, MutableMappingFactory)


def encapsulates(factory: MutableMappingFactory) -> Callable[[_MF], _MF]:
    def decorator(cls):
        cls.mapping_factory = factory
        return cls
    return decorator


class BaseMutableMapping(collections.abc.MutableMapping):
    __slots__ = ('_mapping')

    mapping_factory: Union[MutableMappingFactory, None] = None

    def __init__(self, iterable_or_mapping=(), **kwargs) -> None:
        self._mapping = self.mapping_factory()
        self._mapping.update(iterable_or_mapping, **kwargs)

    def __repr__(self) -> str:
        items = ', '.join(f'{k}={v}' for k, v in self._mapping.items())
        return f'{type(self).__name__}({items})'

    def __getitem__(self, key: Hashable) -> Any:
        return self._mapping[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self._mapping[key] = value

    def __delitem__(self, key: Hashable) -> None:
        del self._mapping[key]

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def __contains__(self, key: Hashable) -> bool:
        return key in self._mapping

    @property
    def data(self) -> types.MappingProxyType:
        return types.MappingProxyType(self._mapping)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self._mapping)

    def __deepcopy__(self):
        return type(self)(copy.deepcopy(self._mapping))

    def __getstate__(self):
        return (self._mapping,)

    def __setstate__(self, state):
        self._mapping = state[0]


class _FromKeysMixin:
    __slots__ = ()

    @classmethod
    def fromkeys(
            cls,
            iterable: Iterable[Hashable],
            value: Optional[Any] = None,
    ):
        return cls((key, value) for key in iterable)


@encapsulates(dict)
class BaseDict(_FromKeysMixin, BaseMutableMapping):
    pass


class _ODMixin:
    def move_to_end(self, key, last=True):
        self._mapping.move_to_end(key, last)

    def popitem(self, last=True):
        self._mapping.popitem(last)


@encapsulates(collections.OrderedDict)
class BaseOrderedDict(_FromKeysMixin, _ODMixin, BaseMutableMapping):
    pass


@encapsulates(litecore.mappings.classes.LastUpdatedOrderedDict)
class BaseLastUpdatedOrderedDict(_FromKeysMixin, _ODMixin, BaseMutableMapping):
    pass


class _DDMixin:
    @property
    def default_factory(self):
        return self._mapping.default_factory

    def __missing__(self, key):
        return self._mapping.__missing__


@encapsulates(collections.defaultdict)
class BaseDefaultDict(_DDMixin, BaseMutableMapping):
    pass


@encapsulates(litecore.mappings.classes.OrderedDefaultDict)
class BaseOrderedDefaultDict(_DDMixin, BaseMutableMapping):
    pass
