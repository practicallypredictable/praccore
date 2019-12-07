import abc
import collections

import litecore.mappings.base
import litecore.mappings.classes


class StringKeyMapping(abc.ABC):
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            msg = f'Keys must be strings; got {key!r}'
            raise litecore.mappings.exceptions.KeyTypeError(msg)
        super().__setitem__(key, value)


@litecore.mappings.base.encapsulates(dict)
class StringKeyDict(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(collections.OrderedDict)
class StringKeyOrderedDict(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(collections.defaultdict)
class StringKeyDefaultDict(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(collections.Counter)
class StringKeyCounter(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(
    litecore.mappings.classes.LastUpdatedOrderedDict)
class StringKeyLastUpdatedOrderedDict(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(
    litecore.mappings.classes.OrderedDefaultDict)
class StringKeyOrderedDefaultDict(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass


@litecore.mappings.base.encapsulates(
    litecore.mappings.classes.OrderedCounter)
class StringKeyOrderedCounter(
        StringKeyMapping,
        litecore.mappings.base.BaseMutableMapping,
):
    pass
