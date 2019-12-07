import collections

from typing import Type

MappingFactory = Type[collections.abc.Mapping]
MutableMappingFactory = Type[collections.abc.MutableMapping]


def deep_merge(original, new):
    if (not isinstance(original, collections.abc.Mapping) or not
            isinstance(new, collections.abc.Mapping)):
        return new
    for key in new:
        if key in original:
            original[key] = deep_merge(original[key], new[key])
        else:
            original[key] = new[key]
    return original
