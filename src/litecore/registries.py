"""Mixin classes and decorators for creating auto-registered classes.

"""
import abc
import collections
import logging
import types

from typing import (
    Any,
    Hashable,
    Iterable,
    Optional,
    Tuple,
    Type,
)

from litecore import LitecoreError as _ErrorBase

log = logging.getLogger(__name__)


class RegistryValueError(_ErrorBase, ValueError):
    """Encountered an invalid value inserting a registry entry."""
    pass


class RegistryTypeError(_ErrorBase, TypeError):
    """Encountered an invalid type while inserting a registry entry."""
    pass


class RegistryBase(abc.ABC, collections.abc.Mapping):
    """

    """
    _mapping_factory = dict

    def __init__(
            self,
            iterable: Optional[Iterable[Tuple[Hashable, Any]]] = None,
            **kwargs,
    ):
        self._registry = self._mapping_factory()
        if iterable:
            for key, obj in iterable:
                self.insert(obj, key=key)
        if kwargs:
            for key, obj in kwargs.items():
                self.insert(obj, key=key)

    @abc.abstractmethod
    def default_key(self, obj: Any) -> Any:
        pass

    @abc.abstractmethod
    def validate_key(self, obj: Any, key: Hashable) -> None:
        if not key:
            raise RegistryValueError('empty registry key for {obj!r}')

    def check_duplicate_key(self, obj: Any, key: Hashable) -> None:
        if key in self._registry:
            dupe_obj = self._registry[key]
            msg = (
                f'attempt to insert key {key!r} for {obj!r}'
                f'duplicates existing key for {dupe_obj!r}'
            )
            raise RegistryValueError(msg)

    def __repr__(self):
        return f'{type(self).__name__}({self._registry!r})'

    def __getitem__(self, key: str):
        return self._registry[key]

    def __len__(self):
        return len(self._registry)

    def __iter__(self):
        return iter(self._registry)

    def view(self) -> types.MappingProxyType:
        """Return a read-only view of the registry contents."""
        return types.MappingProxyType(self._registry)

    def insert(
            self,
            obj: Any,
            *,
            key: Optional[Hashable] = None,
            overwrite: bool = False,
    ) -> None:
        """Add an object to the registry with a given or generated key.

        Arguments:
            obj: the object to be registered

        Keyword Arguments:
            key: string key to map to the registered object (optional;
                default is None, in which case the registry's
                default key getter is used)

        Raises:
            RegistryValueError: an empty key is supplied; or, the key
                already exists
                in the registry and the registry insert_only attribute
                is True.

        Note:
            If the insert_only attribute is False, any overwriting of previous
            entries is logged as as a warning.

        """
        if key is None:
            key = self.default_key(obj)
        self.validate_key(obj, key)
        if not overwrite:
            self.check_duplicate_key(obj, key)
        self._registry[key] = obj

    def register(self, _obj=None, *, key: Optional[Hashable] = None):
        """Decorator to add an object to the registry.

        """
        def decorator(obj: Any):
            self.insert(obj, key=key)
            return obj

        if _obj is None:
            return decorator
        else:
            return decorator(_obj)


class StringKeyRegistry(RegistryBase):
    def validate_key(self, obj: Any, key: str) -> None:
        if not isinstance(key, str):
            msg = f'key must be a string'
            raise RegistryTypeError(msg)
        super().validate_key(obj, key)


class StringKeyClassRegistry(StringKeyRegistry):
    def default_key(self, obj: Type) -> str:
        try:
            return obj.__name__
        except Exception as err:
            msg = f'{obj!r} is not a class'
            raise RegistryTypeError(msg) from err
