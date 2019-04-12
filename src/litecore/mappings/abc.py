import collections
import copy
import itertools
import logging

from typing import (
    Any,
    Callable,
    Hashable,
    Iterator,
    Mapping,
    MutableMapping,
    Tuple,
    Type,
    Union,
)

import litecore.sentinel
import litecore.mappings.exceptions

log = logging.getLogger(__name__)

_NOTHING = litecore.sentinel.create(name='_NOTHING')

# TODO: checking pickling/json/copy/deepcopy for all concrete (__slots__!)
# TODO: dict vs factory in pickling/copy?
# TODO: performance optimiozatinos for all abc methods


def implements(
        factory: Type[MutableMapping],
) -> Callable[[Type[Mapping]], Type[Mapping]]:
    def decorator(cls):
        cls.mapping_factory = factory
        return cls
    return decorator


def all_items(arg, **kwargs) -> Iterator[Tuple[Hashable, Any]]:
    iter_items = None
    if arg:
        if isinstance(arg, collections.abc.Mapping):
            iter_items = arg.items()
        else:
            iter_items = iter(arg)
    if kwargs:
        if iter_items:
            iter_items = itertools.chain(iter_items, kwargs.items())
        else:
            iter_items = kwargs.items()
    return iter_items or iter(())


class BaseMapping(collections.abc.Mapping):
    __slots__ = ('_mapping')

    mapping_factory: Union[Type[MutableMapping], None] = None

    def __init__(self, iterable_or_mapping=(), **kwargs) -> None:
        try:
            self._mapping = self.mapping_factory()
        except TypeError as err:
            msg = (
                f'Cannot instantiate object of type {type(self)} '
                f'with mapping_factory of type {self.mapping_factory}'
            )
            raise NotImplementedError(msg) from err
        self._init_update(iterable_or_mapping, **kwargs)

    # quasi-interface methods
    # so subclases can modify internal mapping object and overload with hooks
    def _set_item(self, key, value):
        self._mapping[key] = value

    def _del_item(self, key):
        del self._mapping[key]

    def _init_update(self, iterable_or_mapping, **kwargs):
        for key, value in all_items(iterable_or_mapping, **kwargs):
            self._set_item(key, value)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._mapping!r})'

    def __getitem__(self, key: Hashable) -> Any:
        return self._mapping[key]

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

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

    @classmethod
    def fromkeys(cls, iterable, value=None):
        try:
            items = cls.mapping_factory().fromkeys(iterable, value)
        except AttributeError:
            items = dict.fromkeys(iterable, value)
        return cls(items)


class BaseMutableMapping(BaseMapping, collections.abc.MutableMapping):
    __slots__ = ()

    def __setitem__(self, key: Hashable, value: Any) -> None:
        super()._set_item(key, value)

    def __delitem__(self, key: Hashable) -> None:
        super()._del_item(key)


class TransformedMapping(BaseMapping):
    __slots__ = ('_transform')

    def __init__(self, transform, iterable_or_mapping=(), **kwargs):
        super().__init__(iterable_or_mapping, **kwargs)
        self._transform = transform

    def __getitem__(self, key):
        return super().__getitem__(self._transform(key))

    def __iter__(self):
        return (orig_key for orig_key, value in super().values())

    def transformed_items(self):
        return ((key, value[1]) for key, value in super().items())

    def __eq__(self, other) -> bool:
        if not isinstance(other, collections.abc.Mapping):
            return NotImplemented
        if len(self) != len(other):
            return False
        other = type(self)(other)
        other_items = other.mapping_factory(other.transformed_items())
        return self.mapping_factory(self.transformed_items()) == other_items


class TransformedMutableMapping(TransformedMapping, BaseMutableMapping):
    __slots__ = ()

    def __setitem__(self, key, value):
        super().__setitem__(self._transform(key), (key, value))

    def __delitem__(self, key):
        super().__delitem__(self._transform(key))


# TODO: checking pickling/json/copy/deepcopy for all concrete (__slots__!)
# TODO: dict vs factory in pickling/copy?
# TODO: performance optimiozatinos for all abc methods
# TODO: need optimized __eq__? hashable?
