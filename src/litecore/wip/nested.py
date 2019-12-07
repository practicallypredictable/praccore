import abc
import collections.abc
import dataclasses
import enum
import inspect
import itertools

from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)

import litecore.utils
from litecore.sentinels import NO_VALUE as _NO_VALUE

# TODO: fix str()?


class ClassMarkerFlag(enum.Flag):
    NONE = 0
    MAPPING = enum.auto()
    SEQUENCE = enum.auto()
    SET = enum.auto()
    NAMED_TUPLE = enum.auto()
    DATA_CLASS = enum.auto()
    CLASS = enum.auto()
    HAS_ATTRIBUTES = CLASS | DATA_CLASS | NAMED_TUPLE
    SERIALIZED_AS_DICT = MAPPING | HAS_ATTRIBUTES
    SERIALIZED_AS_LIST = SET | SEQUENCE
    ALL = MAPPING | SEQUENCE | SET | NAMED_TUPLE | DATA_CLASS | CLASS

    @classmethod
    def from_object(
            cls,
            obj: Any,
            *,
            primitives: Optional[Tuple[Type, ...]] = None,
    ) -> 'ClassMarkerFlag':
        # TODO: handle ASTs?
        if litecore.utils.is_dataclass_instance(obj):
            return cls.DATA_CLASS
        elif litecore.utils.is_namedtuple_instance(obj):
            return cls.NAMED_TUPLE
        elif isinstance(obj, collections.abc.Mapping):
            return cls.MAPPING
        elif litecore.utils.is_iterable(obj):
            if litecore.utils.is_chars(obj):
                return cls.NONE
            elif primitives is not None and isinstance(obj, primitives):
                return cls.NONE
            else:
                if isinstance(obj, collections.abc.Set):
                    return cls.SET
                elif isinstance(obj, collections.abc.Sequence):
                    return cls.SEQUENCE
                else:
                    msg = f'incorrectly categorized iterable object {obj!r}'
                    raise TypeError(msg)
        elif inspect.isclass(obj):
            return cls.CLASS
        else:
            return cls.NONE


def filter_items(
        items: Iterator[Tuple[str, Any]],
        *,
        skip_private: bool,
) -> Iterator[Tuple[Hashable, Any]]:
    for key, value in items:
        skip = key.startswith('__')
        skip = skip or (skip_private and key.startswith('_'))
        skip = skip or litecore.utils.is_function(value)
        if not skip:
            yield key, value


def _iter_mapping(obj: Any):
    return obj.items()


def _iter_collection(obj: Any):
    return enumerate(obj)


def _iter_namedtuple(obj: Any):
    return obj._asdict().items()


def _iter_dataclass(obj: Any):
    return dataclasses.asdict(obj).items()


def _iter_class(obj: Any):
    try:
        slots_iter = (
            (slot, getattr(obj, slot))
            for slot in getattr(obj, '__slots__')
        )
    except AttributeError:
        slots_iter = iter(())
    return itertools.chain(vars(obj).items(), slots_iter)


_ITERATORS = {
    ClassMarkerFlag.MAPPING: _iter_mapping,
    ClassMarkerFlag.SEQUENCE: _iter_collection,
    ClassMarkerFlag.SET: _iter_collection,
    ClassMarkerFlag.NAMED_TUPLE: _iter_namedtuple,
    ClassMarkerFlag.DATA_CLASS: _iter_dataclass,
    ClassMarkerFlag.CLASS: _iter_class,
}


def classify(
        obj: Any,
        *,
        primitives: Optional[Tuple[Type, ...]] = None,
        skip_private: bool = True,
) -> Tuple[Iterator[Any], ClassMarkerFlag]:
    flag = ClassMarkerFlag.from_object(obj, primitives=primitives)
    iterate_items = _ITERATORS.get(flag, None)
    if iterate_items is None:
        return iter(()), ClassMarkerFlag.NONE
    items = (item for item in iterate_items(obj))
    if flag & ClassMarkerFlag.HAS_ATTRIBUTES:
        items = filter_items(items, skip_private=skip_private)
    return flag, items


class ClassMarker(abc.ABC):
    def __init__(self, *, metadata: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.metadata = metadata

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'metadata={self.metadata!r}'
            f')>'
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return all(
            self.metadata[key] == other.metadata[key]
            for key in ('module', 'qualname')
        )

    @staticmethod
    def make_metadata_from_object(obj: Any, **kwargs):
        cls = type(obj)
        metadata = {
            'module': cls.__module__,
            'qualname': cls.__qualname__,
        }
        metadata.update(**kwargs)
        return metadata


class SequenceItem(ClassMarker):
    def __init__(self, *, index: int, **kwargs):
        super().__init__(**kwargs)
        self.index = index

    def __repr__(self):
        s = super().__repr__().replace(')>', '')
        return f'{s}, index={self.index!r})>'

    def __eq__(self, other):
        eq = super().__eq__(other)
        if eq is not True:
            return eq
        return self.index == other.index


class SetItem(ClassMarker):
    def __init__(self, *, item: Hashable, **kwargs):
        super().__init__(**kwargs)
        self.item = item

    def __repr__(self):
        s = super().__repr__().replace(')>', '')
        return f'{s}, item={self.item!r})>'

    def __eq__(self, other):
        eq = super().__eq__(other)
        if eq is not True:
            return eq
        return self.item == other.item


class KeyMarker(ClassMarker):
    def __init__(self, *, key: Hashable, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    def __repr__(self):
        s = super().__repr__().replace(')>', '')
        return f'{s}, key={self.key!r})>'

    def __eq__(self, other):
        eq = super().__eq__(other)
        if eq is not True:
            return eq
        return self.key == other.key


class MappingKey(KeyMarker):
    pass


class AttributeMarker(ClassMarker):
    def __init__(self, *, attr: Any, **kwargs):
        super().__init__(**kwargs)
        self.attr = attr

    def __repr__(self):
        s = super().__repr__().replace(')>', '')
        return f'{s}, attr={self.attr!r})>'

    def __eq__(self, other):
        eq = super().__eq__(other)
        if eq is not True:
            return eq
        return self.attr == other.attr


class ClassAttribute(AttributeMarker):
    pass


class NamedTupleField(AttributeMarker):
    pass


class DataClassField(AttributeMarker):
    pass


class RecursiveMarker(ClassMarker):
    def __init__(
            self,
            *,
            obj_id: int,
            path: Optional[Tuple] = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.obj_id = obj_id
        self.path = path

    def __repr__(self):
        s = super().__repr__().replace(')>', '')
        if self.path is not None:
            return f'{s}, obj_id={self.obj_id!r}, path={self.path!r})>'
        else:
            return f'{s}, obj_id={self.obj_id!r})>'

    def __eq__(self, other):
        eq = super().__eq__(other)
        if eq is not True:
            return eq
        if self.path is not None:
            return self.path == other.path
        else:
            return True


def _class_attr_factory(obj, path_component, child):
    return ClassAttribute(
        metadata=ClassMarker.make_metadata_from_object(obj),
        attr=path_component,
    )


def _namedtuple_field_factory(obj, path_component, child):
    return NamedTupleField(
        metadata=ClassMarker.make_metadata_from_object(obj),
        attr=path_component,
    )


def _dataclass_field_factory(obj, path_component, child):
    return DataClassField(
        metadata=ClassMarker.make_metadata_from_object(obj),
        attr=path_component,
    )


def _mapping_key_factory(obj, path_component, child):
    return MappingKey(
        metadata=ClassMarker.make_metadata_from_object(obj),
        key=path_component,
    )


def _sequence_item_factory(obj, path_component, child):
    return SequenceItem(
        metadata=ClassMarker.make_metadata_from_object(obj),
        index=path_component,
    )


def _set_item_factory(obj, path_component, child):
    return SetItem(
        metadata=ClassMarker.make_metadata_from_object(obj),
        item=path_component,
    )


_PATH_FACTORIES = {
    ClassMarkerFlag.MAPPING: _mapping_key_factory,
    ClassMarkerFlag.SEQUENCE: _sequence_item_factory,
    ClassMarkerFlag.SET: _set_item_factory,
    ClassMarkerFlag.NAMED_TUPLE: _namedtuple_field_factory,
    ClassMarkerFlag.DATA_CLASS: _dataclass_field_factory,
    ClassMarkerFlag.CLASS: _class_attr_factory,
}


def _get_path_factory(
        flag: ClassMarkerFlag,
        class_markers: ClassMarkerFlag,
) -> Callable:
    if flag & class_markers:
        factory = _PATH_FACTORIES.get(flag, None)
    else:
        factory = None
    return factory


def _tupleize_keys(k1, k2) -> Tuple[Hashable, ...]:
    assert k1 is not None
    if k1 == ():
        return (k2,)
    else:
        return k1 + (k2,)


def flatten(
        obj: Any,
        *,
        path_reducer: Callable[[Hashable], Hashable] = _tupleize_keys,
        primitives: Optional[Tuple[Type, ...]] = None,
        maxlevels: Optional[int] = None,
        skip_private: bool = True,
        class_markers: ClassMarkerFlag = ClassMarkerFlag.NONE,
        _path=(),
        _memo=None,
        _level=None,
):
    if _memo is None:
        _memo = dict()
    if maxlevels is not None:
        if _level is None:
            _level = 0
        elif _level > maxlevels:
            yield obj
        else:
            next_level = _level + 1
    else:
        next_level = None
    flag, items = classify(
        obj,
        primitives=primitives,
        skip_private=skip_private,
    )
    assert flag is not None
    if flag is not ClassMarkerFlag.NONE:
        path_factory = _get_path_factory(flag, class_markers)
        if id(obj) not in _memo:
            _memo[id(obj)] = _path
            for path_component, child in items:
                if path_factory is not None:
                    path_component = path_factory(obj, path_component, child)
                for item in flatten(
                        child,
                        path_reducer=path_reducer,
                        primitives=primitives,
                        maxlevels=maxlevels,
                        skip_private=skip_private,
                        class_markers=class_markers,
                        _path=path_reducer(_path, path_component),
                        _memo=_memo,
                        _level=next_level,
                ):
                    yield item
            del _memo[id(obj)]
        else:
            yield _path, RecursiveMarker(
                metadata=ClassMarker.make_metadata_from_object(obj),
                obj_id=id(obj),
                path=_memo[id(obj)],
            )
    else:
        yield _path, obj


def recursive_equality(
        one: Any,
        other: Any,
        *,
        path_reducer: Callable[[Hashable], Hashable] = _tupleize_keys,
        primitives: Optional[Tuple[Type, ...]] = None,
        skip_private: bool = True,
) -> bool:
    one_items = flatten(
        one,
        path_reducer=path_reducer,
        primitives=primitives,
        skip_private=skip_private,
    )
    other_items = flatten(
        other,
        path_reducer=path_reducer,
        primitives=primitives,
        skip_private=skip_private,
    )
    return all(x == y for x, y in itertools.zip_longest(
        one_items,
        other_items,
        fillvalue=_NO_VALUE,
    ))


def serialize(
        obj: Any,
        *,
        metadata_key: Optional[str] = None,
        primitives: Optional[Tuple[Type]] = None,
        skip_private: bool = True,
        _memo=None,
) -> Union[List[Any], Dict[Hashable, Any]]:
    if _memo is None:
        _memo = set()
    if id(obj) not in _memo:
        flag, items = classify(
            obj,
            primitives=primitives,
            skip_private=skip_private,
        )
        assert flag is not None
        if flag & ClassMarkerFlag.SERIALIZED_AS_LIST:
            _memo.add(id(obj))
            result = [
                serialize(
                    item,
                    metadata_key=metadata_key,
                    primitives=primitives,
                    skip_private=skip_private,
                    _memo=_memo,
                ) for index, item in items
            ]
            _memo.remove(id(obj))
        elif flag & ClassMarkerFlag.SERIALIZED_AS_DICT:
            _memo.add(id(obj))
            result = {
                key: serialize(
                    value,
                    metadata_key=metadata_key,
                    primitives=primitives,
                    skip_private=skip_private,
                    _memo=_memo,
                ) for key, value in items
            }
            _memo.remove(id(obj))
            if flag.is_class and metadata_key is not None:
                result[metadata_key] = ClassMarker.make_metadata_from_object(obj)
        else:
            result = obj
    else:
        result = RecursiveMarker(
            metadata=ClassMarker.make_metadata_from_object(obj),
            obj_id=id(obj),
        )
    return result


# def modify(
#         obj: Any,
#         *,
#         modify_key: Callable = lambda x: x,
#         modify_value: Callable = lambda x, original_key: x,
#         mapping_factory: Callable = None,
#         iterable_factory: Callable = None,
#         _memo=None,
# ):
#     if _memo is None:
#         _memo = set()
#     if litecore.check.is_mapping(obj):
#         _memo.add(id(obj))
#         factory = type(obj) if mapping_factory is None else mapping_factory
#         new_obj = factory()
#         for key, value in obj.items():
#             new_obj[modify_key(key)] = modify_value(
#                 modify(
#                     value,
#                     modify_key=modify_key,
#                     modify_value=modify_value,
#                     mapping_factory=mapping_factory,
#                     iterable_factory=iterable_factory,
#                     _memo=_memo,
#                 ),
#                 original_key=key,
#             )
#         _memo.remove(id(obj))
#     elif litecore.check.is_iterable_but_do_not_recurse(obj):
#         _memo.add(id(obj))
#         factory = type(obj) if iterable_factory is None else iterable_factory
#         new_obj = factory(
#             modify(
#                 value,
#                 modify_key=modify_key,
#                 modify_value=modify_value,
#                 mapping_factory=mapping_factory,
#                 iterable_factory=iterable_factory,
#                 _memo=_memo,
#             ) for value in obj
#         )
#         _memo.remove(id(obj))
#     else:
#         return obj
#     return new_obj
