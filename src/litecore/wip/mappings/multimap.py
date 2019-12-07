import abc
import collections
import logging

from typing import (
    Iterable,
    Iterator,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Optional,
    Tuple,
    Type,
)

from litecore._types import KT, VT, HVT

log = logging.getLogger(__name__)


def make_sequence_mapping(
        *,
        mapping_factory: Type[MutableMapping] = collections.defaultdict,
        factory: Type[MutableSequence] = list,
        items: Optional[Iterable[Tuple[KT, VT]]] = None,
):
    mapping = mapping_factory(factory)
    if items is not None:
        for key, value in items:
            mapping[key].append(value)
    return mapping


def make_set_mapping(
        *,
        mapping_factory: Type[MutableMapping] = collections.defaultdict,
        factory: Type[MutableSet] = set,
        items: Optional[Iterable[Tuple[KT, VT]]] = None,
):
    mapping = mapping_factory(factory)
    if items is not None:
        for key, value in items:
            mapping[key].add(value)
    return mapping


class MultiMapping(collections.abc.Mapping):
    def __init__(
            self,
            *,
            create_mapping,
            mapping_factory,
            factory,
            items,
    ) -> None:
        self._factory = factory
        self._mapping = create_mapping(
            mapping_factory=mapping_factory,
            factory=factory,
            items=items,
        )

    @property
    def factory(self):
        return self._factory

    @property
    def len_all_items(self) -> int:
        return sum(len(key_items) for key, key_items in self._mapping.items())

    @property
    def all_items(self):
        for key, key_items in self._mapping.items():
            for item in key_items:
                yield (key, item)

    @property
    def all_values(self):
        for key, value in self.all_items:
            yield value

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'mapping_factory={type(self._mapping)!r}'
            f', factory={self._factory!r}'
            f', items={self._mapping!r}'
            f')'
        )

    @abc.abstractmethod
    def copy(self):
        pass

    @abc.abstractmethod
    def copy_frozen(self):
        pass


class MultiMutableMapping(MultiMapping, collections.abc.MutableMapping):
    pass


class _MappingSharedMixin:
    def __getitem__(self, key: KT) -> VT:
        return self._mapping[key]

    def __iter__(self) -> Iterator[Tuple[KT, VT]]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)


class _MutableMappingSharedMixin:
    def __delitem__(self, key: KT):
        del self._mapping[key]


class _SequenceMappingBaseMixin:
    def __init__(
            self,
            *,
            mapping_factory: Type[MutableMapping] = collections.defaultdict,
            factory: MutableSequence = list,
            items: Optional[Iterable[Tuple[KT, VT]]] = None,
    ) -> None:
        super().__init__(
            create_mapping=make_sequence_mapping,
            mapping_factory=mapping_factory,
            factory=factory,
            items=items,
        )

    def copy(self):
        return type(self)(
            create_mapping=make_sequence_mapping,
            mapping_factory=type(self._mapping),
            factory=type(self.factory),
            items=self.all_items,
        )

    def copy_frozen(self):
        return type(self)(
            create_mapping=make_sequence_mapping,
            mapping_factory=type(self._mapping),
            factory=tuple,
            items=self.all_items,
        )


class _SetMappingBaseMixin:
    def __init__(
            self,
            *,
            mapping_factory: Type[MutableMapping] = collections.defaultdict,
            factory: MutableSet = set,
            items: Optional[Iterable[Tuple[KT, HVT]]] = None,
    ) -> None:
        super().__init__(
            create_mapping=make_set_mapping,
            mapping_factory=mapping_factory,
            factory=factory,
            items=items,
        )

    def copy(self):
        return type(self)(
            create_mapping=make_set_mapping,
            mapping_factory=type(self._mapping),
            factory=type(self.factory),
            items=self.all_items,
        )

    def copy_frozen(self):
        return type(self)(
            create_mapping=make_set_mapping,
            mapping_factory=type(self._mapping),
            factory=frozenset,
            items=self.all_items,
        )


class MultiSequenceMapping(
        _SequenceMappingBaseMixin,
        _MappingSharedMixin,
        MultiMapping,
):
    pass


class MultiMutableSequenceMapping(
        _SequenceMappingBaseMixin,
        _MutableMappingSharedMixin,
        _MappingSharedMixin,
        MultiMutableMapping,
):
    def __setitem__(self, key: KT, value: VT):
        self._mapping[key].append(value)


class MultiSetMapping(
        _SetMappingBaseMixin,
        _MappingSharedMixin,
        MultiMapping,
):
    pass


class MultiMutableSetMapping(
        _SetMappingBaseMixin,
        _MutableMappingSharedMixin,
        _MappingSharedMixin,
        MultiMutableMapping,
):
    def __setitem__(self, key: KT, value: HVT):
        self._mapping[key].add(value)
