import abc
import collections.abc

from typing import (
    Any,
    Callable,
    Hashable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    Type,
)

import litecore.utils


class Marker(abc.ABC):
    @abc.abstractmethod
    def __eq__(self, other):
        pass


class SequenceItem(Marker):
    def __init__(self, *, class_name: str, index: int, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.index = index

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'class_name={self.class_name!r}'
            f', index={self.index!r}'
            f')>'
        )

    def __eq__(self, other):
        try:
            return self.class_name == other.class_name and self.index == other.index
        except (AttributeError, TypeError):
            return NotImplemented


class SetItem(Marker):
    def __init__(self, *, class_name: str, item: Hashable, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.item = item

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'class_name={self.class_name!r}'
            f', item={self.item!r}'
            f')>'
        )

    def __eq__(self, other):
        try:
            return self.class_name == other.class_name and self.item == other.item
        except (AttributeError, TypeError):
            return NotImplemented


class AttributeMarker(Marker):
    def __init__(self, *, class_name: str, attr: Any, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.attr = attr

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'class_name={self.class_name!r}'
            f', attr={self.attr!r}'
            f')>'
        )

    def __eq__(self, other):
        try:
            return self.class_name == other.class_name and self.attr == other.attr
        except (AttributeError, TypeError):
            return NotImplemented


class KeyMarker(Marker):
    def __init__(self, *, class_name: str, key: Hashable, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.key = key

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'class_name={self.class_name!r}'
            f', key={self.key!r}'
            f')>'
        )

    def __eq__(self, other):
        try:
            return self.class_name == other.class_name and self.key == other.key
        except (AttributeError, TypeError):
            return NotImplemented


class ClassAttribute(AttributeMarker):
    pass


class NamedTupleField(AttributeMarker):
    pass


class DataClassField(AttributeMarker):
    pass


class MappingKey(KeyMarker):
    pass


class RecursiveMarker(Marker):
    def __init__(
            self,
            *,
            object_id: int,
            object_type: Type,
            path: Optional[Tuple] = None):
        self.object_id = object_id
        self.object_type = object_type
        self.path = path

    def __repr__(self):
        if self.path is not None:
            return (
                f'<{type(self).__name__}('
                f'object_id={self.object_id!r}'
                f', object_type={self.object_type!r}'
                f', path={self.path!r}'
                f')>'
            )
        else:
            return f'<{type(self).__name__}({self.object_type!r}>'

    def __eq__(self, other):
        try:
            if self.object_type is not other.object_type:
                return False
            if self.path is not None:
                return self.path == other.path
        except (AttributeError, TypeError):
            return NotImplemented


def _filter_keys(items: Iterator[Tuple[str, Any]], skip_private: bool):
    for key, value in items:
        skip = key.startswith('__')
        skip = skip or (skip_private and key.startswith('_'))
        skip = skip or litecore.utils.isfunction(value)
        if not skip:
            yield key, value


def _iter_mapping(obj: Any, skip_private: bool):
    return obj.items()


def _iter_collection(obj: Any, skip_private: bool):
    return enumerate(obj)


def _iter_namedtuple(obj: Any, skip_private: bool):
    yield from _filter_keys(obj._asdict().items(), skip_private)


def _iter_class_items(obj: Any, skip_private: bool):
    yield from _filter_keys(vars(obj).items(), skip_private)
    try:
        slots = (
            (slot, getattr(obj, slot))
            for slot in getattr(obj, '__slots__')
        )
    except AttributeError:
        pass
    else:
        yield from _filter_keys(slots, skip_private)


def _class_attr_factory(obj, path_component, child):
    return ClassAttribute(
        class_name=type(obj).__qualname__,
        attr=path_component,
    )


def _namedtuple_field_factory(obj, path_component, child):
    return NamedTupleField(
        class_name=type(obj).__qualname__,
        attr=path_component,
    )


def _mapping_key_factory(obj, path_component, child):
    return MappingKey(
        class_name=type(obj).__name__,
        key=path_component,
    )


def _sequence_item_factory(obj, path_component, child):
    return SequenceItem(
        class_name=type(obj).__qualname__,
        index=path_component,
    )


def _set_item_factory(obj, path_component, child):
    return SetItem(
        class_name=type(obj).__qualname__,
        item=path_component,
    )


def _get_iterator(
        obj: Any,
        *,
        do_not_iterate: Optional[Tuple[Type, ...]],
        show_class_attr: bool,
        show_namedtuple_field: bool,
        show_dataclass_field: bool,
        show_mapping_key: bool,
        show_sequence_item: bool,
        show_set_item: bool,
) -> Tuple[Callable, Callable]:
    if do_not_iterate is not None:
        do_not_iterate = tuple([str, bytes, bytearray] + list(do_not_iterate))
    else:
        do_not_iterate = (str, bytes, bytearray)
    iterator = None
    path_factory = None
    # TODO: handle ASTs?
    # TODO: handle dataclasses
    if isinstance(obj, collections.abc.Mapping):
        iterator = _iter_mapping
        if show_mapping_key:
            path_factory = _mapping_key_factory
    elif hasattr(obj, '_asdict'):
        iterator = _iter_namedtuple
        if show_namedtuple_field:
            path_factory = _namedtuple_field_factory
    elif hasattr(obj, '__iter__'):
        if not isinstance(obj, do_not_iterate):
            iterator = _iter_collection
            if show_set_item and isinstance(obj, collections.abc.Set):
                path_factory = _set_item_factory
            elif show_sequence_item:
                path_factory = _sequence_item_factory
    elif hasattr(obj, '__dict__') or hasattr(obj, '__slots__'):
        iterator = _iter_class_items
        if show_class_attr:
            path_factory = _class_attr_factory
    return iterator, path_factory


def flatten(
        obj: Any,
        *,
        do_not_iterate: Optional[Tuple[Type]] = None,
        skip_private: bool = True,
        show_class_attr: bool = True,
        show_namedtuple_field: bool = True,
        show_dataclass_field: bool = True,
        show_mapping_key: bool = True,
        show_set_item: bool = True,
        show_sequence_item: bool = True,
        _path=(),
        _memo=None,
):
    if _memo is None:
        _memo = dict()
    iterator, path_factory = _get_iterator(
        obj,
        do_not_iterate=do_not_iterate,
        show_class_attr=show_class_attr,
        show_namedtuple_field=show_namedtuple_field,
        show_dataclass_field=show_dataclass_field,
        show_mapping_key=show_mapping_key,
        show_set_item=show_set_item,
        show_sequence_item=show_sequence_item,
    )
    if iterator is not None:
        if id(obj) not in _memo:
            _memo[id(obj)] = _path
            for path_component, child in iterator(obj, skip_private):
                if path_factory is not None:
                    path_component = path_factory(obj, path_component, child)
                for item in flatten(
                        child,
                        do_not_iterate=do_not_iterate,
                        skip_private=skip_private,
                        show_class_attr=show_class_attr,
                        show_namedtuple_field=show_namedtuple_field,
                        show_dataclass_field=show_dataclass_field,
                        show_mapping_key=show_mapping_key,
                        show_set_item=show_set_item,
                        show_sequence_item=show_sequence_item,
                        _path=_path + (path_component,),
                        _memo=_memo,
                ):
                    yield item
            del _memo[id(obj)]
        else:
            yield _path, RecursiveMarker(
                object_id=id(obj),
                object_type=type(obj),
                path=_memo[id(obj)],
            )
    else:
        yield _path, obj


def _process_mapping(
        obj: Any,
        *,
        _memo,
        classkey: Optional[str] = None,
        skip_private: bool,
):
    items = {}
    for key, value in obj.items():
        skip_key = skip_private and key.startswith('_')
        skip_key = skip_key or key.startswith('__')
        skip_value = callable(value)
        if not skip_key and not skip_value:
            items[key] = ObjectGraph(
                value,
                _memo=_memo,
                classkey=classkey,
                skip_private=skip_private,
            )
    return items


def _process_special(
        obj: Any,
        mapping: Mapping,
        *,
        _memo,
        classkey: Optional[str] = None,
        skip_private: bool,
):
    _memo.add(id(obj))
    items = _process_mapping(
        mapping,
        _memo=_memo,
        classkey=classkey,
        skip_private=skip_private,
    )
    _memo.remove(id(obj))
    if classkey is not None and hasattr(obj, '__class__'):
        items[classkey] = obj.__class__.__name__
    return items


class ObjectGraph:
    def __new__(
            cls,
            obj: Any,
            *,
            _memo=None,
            classkey: Optional[str] = '__class__',
            skip_private: bool = False,
    ):
        self = super().__new__(cls)
        if _memo is None:
            _memo = set()
        if id(obj) not in _memo:
            if isinstance(obj, (str, bytes, bytearray)):
                self = obj
            elif isinstance(obj, collections.abc.Mapping):
                _memo.add(id(obj))
                self.__dict__ = _process_mapping(
                    obj,
                    _memo=_memo,
                    classkey=classkey,
                    skip_private=skip_private,
                )
                _memo.remove(id(obj))
            elif hasattr(obj, '_ast'):
                self.__dict__ = _process_special(
                    obj,
                    obj._ast(),
                    _memo=_memo,
                    classkey=classkey,
                    skip_private=skip_private,
                )
            elif hasattr(obj, '_asdict'):
                self.__dict__ = _process_special(
                    obj,
                    obj._asdict(),
                    _memo=_memo,
                    classkey=classkey,
                    skip_private=skip_private,
                )
            elif hasattr(obj, '__iter__'):
                _memo.add(id(obj))
                self = [
                    ObjectGraph(
                        item,
                        _memo=_memo,
                        classkey=classkey,
                        skip_private=skip_private,
                    ) for item in obj
                ]
                _memo.remove(id(obj))
            elif hasattr(obj, '__dict__'):
                self.__dict__ = _process_special(
                    obj,
                    vars(obj),
                    _memo=_memo,
                    classkey=classkey,
                    skip_private=skip_private,
                )
            elif hasattr(obj, '__slots__'):
                slots = {
                    slot: getattr(obj, slot)
                    for slot in getattr(obj, '__slots__')
                    if not slot.startswith('__')
                }
                self.__dict__ = _process_special(
                    obj,
                    slots,
                    _memo=_memo,
                    classkey=classkey,
                    skip_private=skip_private,
                )
            else:
                # TODO: log warning?
                self = obj
        else:
            self = RecursiveMarker(obj)
        return self

    def __repr__(self):
        return f'{type(self).__name__}({self.__dict__!r})'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self == other
