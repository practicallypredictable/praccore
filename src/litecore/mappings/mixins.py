import logging

import litecore.sentinel
import litecore.diagnostics
import litecore.mappings.exceptions

log = logging.getLogger(__name__)
_NOTHING = litecore.sentinel.create(name='_NOTHING')


class StringKeyOnlyMixin:
    __slots__ = ()

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            msg = f'Keys must be strings; got {key!r}'
            raise litecore.mappings.exceptions.KeyTypeError(msg)
        super().__setitem__(key, value)


class SetKeyOnceMixin:
    __slots__ = ()

    def __setitem__(self, key, value):
        existing = super().get(key, _NOTHING)
        if existing is not _NOTHING:
            msg = (
                f'Key {key!r} is already set; '
                f'value is {existing!r}; '
                f'attempted to set value to {value!r}'
            )
            raise KeyError(msg)
        super().__setitem__(key, value)


def _log_get_item(logger, level, instance, key):
    msg = 'Getting value for key %r in mapping of type %r'
    logger.log(level, msg, key, type(instance))


def _log_set_item(logger, level, instance, key, value):
    msg = 'Setting value for key %r to %r in mapping of type %r'
    logger.log(level, msg, key, value, type(instance))


def _log_del_item(logger, level, instance, key):
    msg = 'Deleting key %r in mapping of type %r'
    logger.log(level, msg, key, type(instance))


# This decorator function has an informative docstring
logged_mapping = litecore.diagnostics.make_logged_collection_decorator(
    log_get=_log_get_item,
    log_set=_log_set_item,
    log_del=_log_del_item,
)

# Do not make the factory public, as the primary purpose is to create
#   the utility mixin below set to DEBUG level. Users of the module can
#   create their own factory if their needs are different.
_logged_mapping_mixin_factory = litecore.diagnostics.make_logged_mixin_factory(
    log_get=_log_get_item,
    log_set=_log_set_item,
    log_del=_log_del_item,
)


# TODO: make docstring
LoggedMappingMixin = _logged_mapping_mixin_factory(name='LoggedMappingMixin')
"""Mixin class to log all item access at DEBUG level.

This class is intended to be mixed-in with a class that implements either
the Mapping (read-only) or MutableMapping interfaces. It is not optimized
for the read-only Mapping interface, since this is intended primarily for
debugging. If performance is critical for some reason , or if another logging
level is desired, create a modified mixin factory with the desired logging
level, and only include the log_get or other specific functions; this will
optimize out the unneeded methods from the returned mixin class.

The mixin assumes the existence of a logging.Logger object accessible at the
instance level (e.g., via a property) with the name 'logger'. See the
litecore.diagnostics module for the LoggedMixin and some other ways to
implement this, or roll your own.

Also note that the logged_mapping() decorator herein will be more optimized
than this mixin, since it can do the necessary optimizations at time of class
creation.

"""
