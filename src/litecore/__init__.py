"""Light-weight utility classes and functions for Python 3.6 and higher.

"""

__version__ = '0.2.0'

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LitecoreError(Exception):
    """Base class for all exceptions raised by this package."""
    pass
