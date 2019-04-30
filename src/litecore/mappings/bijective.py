import collections
import dataclasses
import logging
import types

from typing import (
    Any,
    Hashable,
)

import litecore.sentinel
import litecore.transaction
import litecore.mappings.abc
import litecore.mappings.exceptions

log = logging.getLogger(__name__)

_NOTHING = litecore.sentinel.create(name='_NOTHING')


@dataclasses.dataclass(frozen=True)
class _PriorBijectiveItem:
    key: Hashable
    value: Any

    @property
    def has_key(self) -> bool:
        return self.key is not _NOTHING

    @property
    def has_value(self) -> bool:
        return self.value is not _NOTHING


class BijectiveMapping(litecore.mappings.abc.BaseMapping):
    __slots__ = ('_inverse_mapping')

    def __init__(self, iterable_or_mapping=(), **kwargs):
        try:
            self._inverse_mapping = self.mapping_factory()
        except TypeError as err:
            msg = (
                f'Cannot instantiate object of type {type(self)} '
                f'with mapping_factory of type {self.mapping_factory}'
            )
            raise NotImplementedError(msg) from err
        super().__init__(iterable_or_mapping, **kwargs)

    def _get_prior_item(self, key, value=_NOTHING):
        return _PriorBijectiveItem(
            key=self._inverse_mapping.get(value, _NOTHING),
            value=super().get(key, _NOTHING),
        )

    def _delete_from_mapping(self, key, value):
        super()._del_item(key)
        return litecore.transaction.undoer(
            super()._set_item,
            key,
            value,
        )

    def _delete_from_inverse(self, value, key):
        del self._inverse_mapping[value]
        return litecore.transaction.undoer(
            self._inverse_mapping.__setitem__,
            value,
            key,
        )

    def _overwrite_mapping(self, key, value, prior_value=_NOTHING):
        super()._set_item(key, value)
        if prior_value is not _NOTHING:
            return litecore.transaction.undoer(
                super()._set_item,
                key,
                prior_value,
            )
        else:
            return litecore.transaction.undoer(
                super()._del_item,
                key,
            )

    def _overwrite_inverse(self, value, key, prior_key=_NOTHING):
        self._inverse_mapping[value] = key
        if prior_key is not _NOTHING:
            return litecore.transaction.undoer(
                self._inverse_mapping.__setitem__,
                value,
                prior_key,
            )
        else:
            return litecore.transaction.undoer(
                self._inverse_mapping.__delitem__,
                value,
            )

    def _set_item(self, key, value):
        prior_item = self._get_prior_item(key, value)
        if prior_item.has_key and prior_item.has_value:
            if key == prior_item.key and value == prior_item.value:
                return
            else:
                msg = (
                    f'Attempt to map key {key} to value {value} '
                    f'clashes with existing items ({key}, {prior_item.value}) '
                    f'and ({prior_item.key}, {value})'
                )
                raise litecore.mappings.exceptions.OneToOneKeyError(msg)
        with litecore.transaction.TransactionManager() as transaction:
            transaction.prepare()
            if prior_item.has_key:
                transaction.push_undo(
                    self._delete_from_inverse(prior_item.value, key))
            elif prior_item.has_value:
                transaction.push_undo(
                    self._delete_from_mapping(prior_item.key, value))
            transaction.push_undo(
                self._overwrite_mapping(key, value, prior_item.value))
            transaction.push_undo(
                self._overwrite_inverse(value, key, prior_item.key))
            transaction.commit()

    def _del_item(self, key):
        value = super().get(key, _NOTHING)
        if value is _NOTHING:
            return
        with litecore.transaction.TransactionManager() as transaction:
            transaction.prepare()
            transaction.push_undo(self._delete_from_mapping(key, value))
            transaction.push_undo(self._delete_from_inverse(value, key))
            transaction.commit()

    @property
    def inverse(self):
        return types.MappingProxyType(self._inverse_mapping)

    def values(self):
        return self._inverse_mapping.keys()

    def inverse_get(self, key, default=_NOTHING):
        value = self._inverse_mapping.get(key, default)
        if value is _NOTHING:
            raise KeyError(key)
        else:
            return value


class BijectiveMutableMapping(
        BijectiveMapping,
        collections.abc.MutableMapping,
):
    __slots__ = ()

    def __setitem__(self, key: Hashable, value: Any) -> None:
        super()._set_item(key, value)

    def __delitem__(self, key: Hashable) -> None:
        super()._del_item(key)


@litecore.mappings.abc.implements(dict)
class BijectiveDict(BijectiveMutableMapping):
    pass
