"""Light-weight utility classes and functions for Python 3.6 and higher.

"""

__version__ = '0.2.0'

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LitecoreError(BaseException):
    """Base class for exceptions raised by this package.

    Errors encountered in the process of creating objects or calling
    functions in this package will use standard exception types (e.g.,
    passing incorrect arguments will raise a ValueError, etc.) However,
    errors unrelated to the setup of the class or function will be
    raised using non-standard exception types sub-classing this class.

    """
