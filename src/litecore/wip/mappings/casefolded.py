import logging

import litecore.mappings.abc
import litecore.mappings.classes

log = logging.getLogger(__name__)


class CaseInsensitiveMutableMapping(
        litecore.mappings.abc.TransformedMutableMapping,
):
    case_transform = str.casefold

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.case_transform, *args, **kwargs)


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyDict)
class CaseInsensitiveDict(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyOrderedDict)
class CaseInsensitiveOrderedDict(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyLastUpdatedOrderedDict)
class CaseInsensitiveLastUpdatedOrderedDict(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyDefaultDict)
class CaseInsensitiveDefaultDict(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyEnhancedDefaultDict)
class CaseInsensitiveEnhancedDefaultDict(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyCounter)
class CaseInsensitiveCounter(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyEnhancedCounter)
class CaseInsensitiveEnhancedCounter(CaseInsensitiveMutableMapping):
    pass


@litecore.mappings.abc.mapping_factory(
    litecore.mappings.classes.StringKeyOnlyOrderedCounter)
class CaseInsensitiveOrderedCounter(CaseInsensitiveMutableMapping):
    pass
