"""Mixin classes and decorators for creating auto-registered classes.

"""
import collections
import logging
import operator
import types

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
)

from litecore import LitecoreError as _ErrorBase
import litecore.mappings.stringkey
import litecore.mappings.setonce

log = logging.getLogger(__name__)


class StringKeyRegistryMapping(
        litecore.mappings.stringkey.StringKeyDict,
        litecore.mappings.setonce.SetKeyOnceMutableMapping,
):
    """Underlying mapping class for registering objects.

    Keys are constrained to be strings and may only be set once.

    """
    pass


class RegistryValueError(_ErrorBase, ValueError):
    """Encountered an error while attempting to insert a registry entry."""
    pass


class StringKeyRegistry(collections.abc.Mapping):
    """Class for mapping of string keys to objects.

    Keyword Arguments:
        key:
        items: optional

    """
    mapping_factory = StringKeyRegistryMapping
    default_key = operator.attrgetter('__name__')

    def __init__(
            self,
            *,
            key: Optional[Callable[[Any], str]] = None,
            items: Optional[Iterable[Any]] = None,
    ) -> None:
        self.key = key if key is not None else self.default_key
        self._registry = self.mapping_factory()
        if items:
            self._registry.update(items)

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f', key={self.key}'
            f', items={self._registry!r}'
            f')'
        )

    def __getitem__(self, key: str) -> Any:
        return self._registry[key]

    def __len__(self) -> int:
        return len(self._registry)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._registry)

    def view(self) -> types.MappingProxyType:
        """Return a read-only view of the  registry contents."""
        return types.MappingProxyType(self._registry)

    def insert(
            self,
            obj: Any,
            *,
            key: Optional[str] = None,
    ) -> None:
        """Add a class object with a given or generated key to the registry.

        Positional Arguments:
            class_obj: the class object to be registered

        Keyword Arguments:
            key: string key to map to the registered class object;
                optional, default is None, in which case the registry's
                default key getter is used

        Raises:
            RegistryValueError: an empty key is supplied; or, the key already exists
                in the registry and the registry insert_only attribute is True.

        Note:
            If the insert_only attribute is False, any overwriting of previous
            entries is logged as as a warning.

        """
        if key is None:
            try:
                key = self.key(obj)
            except (AttributeError, KeyError, TypeError) as err:
                msg = (
                    f'Could not get key for {obj!r}'
                    f' using key getter {self.key!r}'
                )
                raise RegistryValueError(msg) from err
        if not key:
            msg = f'Empty registry key for {obj!r}'
            raise RegistryValueError(msg)
        try:
            self._registry[key] = obj
        except (ValueError, KeyError, TypeError) as err:
            msg = f'Could not insert registry key {key} for {obj!r}'
            raise RegistryValueError(msg) from err

    def register(
            self,
            _obj: Any = None,
            *,
            key: Optional[str] = None,
    ):
        """Decorator to add an object to the registry.

        """
        def decorator(obj: Any):
            self.insert(obj, key=key)
            return obj

        if _obj is None:
            return decorator
        else:
            return decorator(_obj)


class StringKeyClassRegistry(StringKeyRegistry):
    pass


class StringKeyFunctionRegistry(StringKeyRegistry):
    pass
