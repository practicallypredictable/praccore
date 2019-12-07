import itertools

from typing import (
    Any,
    Hashable,
    Optional,
    Tuple,
)

from litecore.sentinels import NO_VALUE as _NO_VALUE
import litecore.objtype as lcot


class RecursiveMarker:
    def __init__(
            self,
            obj: Any,
            path: Tuple[Hashable, ...],
    ):
        self.obj_type = type(obj)
        self.obj_id = id(obj)
        self.path = path

    def __repr__(self):
        return (
            f'<{type(self).__name__}: '
            f'{self.obj_type!r}'
            f' with id {self.obj_id!r}'
            f'>'
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.obj_type is other.obj_type and self.obj_id == other.obj_id


def flatten(
        obj: Any,
        *,
        maxdepth: Optional[int] = None,
        child_object_getter: lcot.ChildObjectGetter = lcot.child_objects,
        _depth=None,
        _seen=None,
        _path=None,
):
    """

    Examples:

    >>> items = list(range(3))
    >>> items.append(items)
    >>> list(flatten(items))  # doctest: +ELLIPSIS
    [((0,), 0), ((1,), 1), ((2,), 2), ((3,), <RecursiveMarker: <class 'list'> with id ...>)]
    >>> items = {'a': [1, 2, 3], 'b': items}
    >>> list(flatten(items))  # doctest: +ELLIPSIS
    [(('a', 0), 1), ..., (('a', 2), 3), (('b', 0), 0), ..., (('b', 3), <RecursiveMarker: <class 'list'> with id ...>)]
    >>> items = [items]
    >>> items.append(items)
    >>> list(flatten(items))  # doctest: +ELLIPSIS


    """
    if _depth is None:
        _depth = 0
    if _seen is None:
        _seen = {}
    if _path is None:
        _path = ()
    children = child_object_getter(obj)
    deeper = maxdepth is None or _depth < maxdepth
    if children is None or not deeper:
        yield _path, obj
    elif id(obj) in _seen:
        yield _path, RecursiveMarker(obj, _path)
    else:
        _seen[id(obj)] = _path
        for path_component, child in children:
            yield from flatten(
                child,
                maxdepth=maxdepth,
                child_object_getter=child_object_getter,
                _depth=_depth + 1,
                _seen=_seen,
                _path=_path + (path_component,),
            )
        del _seen[id(obj)]


def deep_equality(
        first: Any,
        second: Any,
) -> bool:
    first_items = flatten(
        first,
    )
    second_items = flatten(
        second,
    )
    return all(x == y for x, y in itertools.zip_longest(
        first_items,
        second_items,
        fillvalue=_NO_VALUE,
    ))


# def serialize(
#         obj: Any,
#         *,
#         metadata_key: Optional[str] = None,
#         primitives: Optional[Tuple[Type]] = None,
#         skip_private: bool = True,
#         _memo=None,
# ) -> Union[List[Any], Dict[Hashable, Any]]:
#     if _memo is None:
#         _memo = set()
#     if id(obj) not in _memo:
#         obj_type, items = obj_type_and_items(
#             obj,
#             primitives=primitives,
#             skip_private=skip_private,
#         )
#         if obj_type.serialized_as_list:
#             _memo.add(id(obj))
#             result = [
#                 serialize(
#                     item,
#                     metadata_key=metadata_key,
#                     primitives=primitives,
#                     skip_private=skip_private,
#                     _memo=_memo,
#                 ) for index, item in items
#             ]
#             _memo.remove(id(obj))
#         elif obj_type.serialized_as_dict:
#             _memo.add(id(obj))
#             result = {
#                 key: serialize(
#                     value,
#                     metadata_key=metadata_key,
#                     primitives=primitives,
#                     skip_private=skip_private,
#                     _memo=_memo,
#                 ) for key, value in items
#             }
#             _memo.remove(id(obj))
#             if flag.is_class and metadata_key is not None:
#                 result[metadata_key] = ClassMarker.make_metadata(obj)
#         else:
#             result = obj
#     else:
#         result = RecursiveMarker(obj)
#     return result


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
