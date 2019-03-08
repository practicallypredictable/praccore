"""Mixin classes and decorators for creating auto-registered classes.

"""
__all__ = (
    'ClassRegistry',
)

import collections
import logging
import operator
import types

from typing import (
    Any,
    Callable,
    Hashable,
    Iterator,
    Optional,
    Type,
    Union,
)

log = logging.getLogger(__name__)


class ClassRegistry(collections.abc.Mapping):
    """Mapping of hashable keys to class objects.

    """
    def __init__(
            self,
            *,
            insert_only: bool = True,
            key_getter: Callable[[Type], Hashable] = operator.attrgetter('__name__'),
            factory: Type[collections.abc.MutableMapping] = collections.OrderedDict,
    ) -> None:
        self.insert_only = insert_only
        self.key_getter = key_getter
        self._registry = factory()

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'insert_only={self.insert_only!r}'
            f', key_getter={self.key_getter!r}'
            f', factory={type(self._registry)}'
            f') with {len(self)} registered classes>'
        )

    def __str__(self) -> str:
        return str(self._registry)

    def __getitem__(self, key: Hashable) -> Type:
        return self._registry[key]

    def __len__(self) -> int:
        return len(self._registry)

    def __iter__(self) -> Iterator[Type]:
        return iter(self._registry)

    def view(self) -> types.MappingProxyType:
        """Return a read-only view of the class registry contents."""
        return types.MappingProxyType(self._registry)

    def register_class(
            self,
            class_obj: Type,
            *,
            key: Optional[Hashable] = None,
    ) -> None:
        """Register a class object with a given or generated key.

        Arguments:
            class_obj: the class object to be registered

        Keyword Arguments:
            key: (optional) hashable key to map to the registered class object

        If key is None, a key is generated using the registry's default key
        getter specified at instnatiation of the registry.

        Raises:
            ValueError: an empty key is supplied; or, the key already exists
                in the registry and the registry insert_only attribute is True.

        Note:
            If the insert_only attribute is False, any overwriting of previous
            entries is logged as as a warning.

        """
        if key is None:
            try:
                key = self.key_getter(class_obj)
            except Exception as err:
                msg = (
                    f'Could not get key for class object {class_obj!r}'
                    f' using key getter {self.key_getter!r}'
                )
                raise ValueError(msg) from err
        if not key:
            msg = f'Empty registry key for object {class_obj!r}'
            raise ValueError(msg)
        if key in self._registry:
            if self.insert_only:
                msg = f'Key {key!r} already in insert-only registry'
                raise ValueError(msg)
            else:
                msg = (
                    f'Key {key!r} already in registry {self!r} '
                    f'for object {self._registry[key]!r}; '
                    f'overwriting with new object {class_obj!r}'
                )
                log.warn(msg)
        self._registry[key] = class_obj

    def register(
            self,
            _cls: Type = None,
            *,
            key: Optional[Hashable] = None,
    ) -> :
        """Class decorator to add a class object to the registry.

        """

        def decorator(class_obj: Type):
            self.register_class(class_obj, key)
            return class_obj

        if check.is_class(obj):
            # Decorator invoked directly on the class definition
            key = self.key_getter(obj)
            self.register_class(obj, key)
            return obj
        else:
            # Decorator invoked with the key as an argument
            # The object definition needs to be handled by an inner decorator
            key = obj

            return decorator

    def get(
            self,
            key: Hashable,
            *,
            default: Optional[Type] = None,
    ) -> Union[Type, None]:
        """[summary]

        Arguments:
            key {Hashable} -- [description]

        Keyword Arguments:
            default {Optional[Type]} -- [description] (default: {None})

        Raises:
            KeyError -- [description]

        Returns:
            Union[Type, None] -- [description]
        """

        try:
            return self._registry[key]
        except KeyError as err:
            if default is not None:
                return default
            else:
                msg = f'No key {key!r} in class registry {self!r}'
                raise KeyError(msg) from err
