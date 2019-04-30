import collections.abc
import typing

import litecore.validate.base
import litecore.validate.multistep
import litecore.validate.boolean
import litecore.validate.numbers
import litecore.validate.strings
import litecore.validate.structures
import litecore.validate.schema


def build_schema(obj: typing.Any, *, _memo=None):
    if _memo is None:
        _memo = set()
    if id(obj) not in _memo:
        if isinstance(obj, collections.abc.Set):
            _memo.add(obj)
            items = tuple(build_schema(item, _memo=_memo) for item in obj)
            result = litecore.validate.multistep.Any(*items)
            _memo.remove(obj)
        elif isinstance(obj, tuple):
            _memo.add(obj)
            items = tuple(build_schema(item, _memo=_memo) for item in obj)
            result = litecore.validate.structures.Tuple(*items)
            _memo.remove(obj)
        elif isinstance(obj, collections.abc.Sequence):
            if __debug__:
                if len(obj) != 1:
                    msg = f'sequence should have length 1; got {obj!r}'
                    raise ValueError(msg)
            _memo.add(obj)
            result = litecore.validate.structures.Sequence(
                build_schema(obj[0], _memo=_memo)
            )
            _memo.remove(obj)
        elif isinstance(obj, collections.abc.Mapping):
            _memo.add(obj)
            result = litecore.validate.schema.Schema(
                build_schema(obj, _memo=_memo)
            )
            _memo.remove(obj)
        elif isinstance(obj, litecore.validate.base.Validator):
            result = obj
        elif isinstance(obj, type):
            result = litecore.validate.base.get_validator_for(obj)()
        else:
            msg = f'not sure what to do with object of type {type(obj)!r}'
            raise TypeError(msg)
        return result
    else:
        # TODO: warn?
        return obj
