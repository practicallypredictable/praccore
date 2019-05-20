import enum

import litecore.serialize.asjson  # noqa: F401
import litecore.serialize.standard  # noqa: F401


class Verbosity(enum.Flag):
    """Specifies the level of metadata verbosity in a serialization."""
    NONE = 0
    CLASS_INFO = enum.auto()
    TIME_STAMP = enum.auto()
    ALL = CLASS_INFO | TIME_STAMP
