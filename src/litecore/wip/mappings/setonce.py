import abc
import collections
import logging

from litecore import LitecoreError as _ErrorBase
import litecore.sentinel
import litecore.diagnostics
import litecore.mappings.base
import litecore.mappings.classes

log = logging.getLogger(__name__)

_NOTHING = litecore.sentinel.create(name='_NOTHING')


class DuplicateKeyError(_ErrorBase, ValueError):
    """Encountered an attempt to insert/update an already-existing key.

    Only relevant for mapping types designed to reject such attempts.

    """
    pass


class SetKeyOnceMutableMapping(abc.ABC):
    def __setitem__(self, key, value) -> None:
        existing = super().get(key, _NOTHING)
        if existing is not _NOTHING:
            msg = (
                f'Key {key!r} is already set; '
                f'value is {existing!r}; '
                f'attempted to set value to {value!r}'
            )
            raise DuplicateKeyError(msg)
        super().__setitem__(key, value)

    def force_overwrite(self, key, value) -> None:
        """Delete item if it exists and then add new item in its place."""
        try:
            self.__delitem__(key)
        except KeyError:
            pass
        self.__setitem__(key, value)


@litecore.mappings.base.encapsulates(dict)
class SetKeyOnceDict(
        SetKeyOnceMutableMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(collections.OrderedDict)
class SetKeyOnceOrderedDict(
        SetKeyOnceMutableMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(collections.defaultdict)
class SetKeyOnceDefaultDict(
        SetKeyOnceMutableMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(
    litecore.mappings.classes.LastUpdatedOrderedDict)
class SetKeyOnceLastUpdatedOrderedDict(
        SetKeyOnceMutableMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(
    litecore.mappings.classes.OrderedDefaultDict)
class SetKeyOnceOrderedDefaultDict(
        SetKeyOnceMutableMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass
