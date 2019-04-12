import collections
import logging

from typing import (
    TypeVar,
)

import litecore.mappings

log = logging.getLogger(__name__)


class JSONEncodingABC(collections.abc.MutableMapping):
    pass


JSONEncodingType = TypeVar('JSONEncodingType', bound=JSONEncodingABC)


class JSONEncoding(
        litecore.mappings.StringKeyOnlyMappingMixin,
        dict,
        JSONEncodingABC,
):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class OrderedJSONEncoding(
        litecore.mappings.StringKeyOnlyMappingMixin,
        collections.OrderedDict,
        JSONEncodingABC,
):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
