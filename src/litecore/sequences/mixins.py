import logging

import litecore.diagnostics

log = logging.getLogger(__name__)


def _log_get_item(logger, level, instance, index_or_slice):
    msg = 'Getting value for item %r in sequence of type %r'
    logger.log(level, msg, index_or_slice, type(instance))


def _log_set_item(logger, level, instance, index_or_slice, value):
    msg = 'Setting value for item %r to %r in sequence of type %r'
    logger.log(level, msg, index_or_slice, value, type(instance))


def _log_del_item(logger, level, instance, index_or_slice):
    msg = 'Deleting item %r in sequence of type %r'
    logger.log(level, msg, index_or_slice, type(instance))


logged_sequence = litecore.diagnostics.make_logged_collection_decorator(
    log_get=_log_get_item,
    log_set=_log_set_item,
    log_del=_log_del_item,
)
# This decorator function has an informative docstring

_logged_sequence_mixin_factory = litecore.diagnostics.make_logged_mixin_factory(
    log_get=_log_get_item,
    log_set=_log_set_item,
    log_del=_log_del_item,
)
# Do not make the factory public, as the primary purpose is to create
#   the utility mixin below set to DEBUG level. Users of the module can
#   create their own factory if their needs are different.

LoggedSequenceMixin = _logged_sequence_mixin_factory(name='LoggedSequenceMixin')
"""Mixin class to log all item access at DEBUG level.

This class is intended to be mixed-in with a class that implements either
the Sequence (read-only) or MutableSequence interfaces. It is not optimized
for the read-only Sequence interface, since this is intended primarily for
debugging. If performance is critical for some reason , or if another logging
level is desired, create a modified mixin factory with the desired logging
level, and only include the log_get or other specific functions; this will
optimize out the unneeded methods from the returned mixin class.

The mixin assumes the existence of a logging.Logger object accessible at the
instance level (e.g., via a property) with the name 'logger'. See the
litecore.diagnostics module for the LoggedMixin and some other ways to
implement this, or roll your own.

Also note that the logged_sequence() decorator herein will be more optimized
than this mixin, since it can do the necessary optimizations at time of class
creation.

"""
