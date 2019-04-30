"""Convenience functions for mappings.

Unless noted otherwise, each function returns an iterator of (key, value)
tuples in the same order as iteration over the keys of the original mapping
argument. These tuples may then be used to instantiate whatever type of mapping
the user desires.

"""
import collections
import itertools
import logging

from typing import (
    Any,
    Callable,
    Collection,
    Hashable,
    Iterator,
    Mapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Tuple,
    Type,
)

from litecore._types import KT, VT, HVT
import litecore.check

log = logging.getLogger(__name__)


def keyed_values(iterable, *, by):
    return ((by(value), value) for value in iterable)


def keep_keys(mapping, *, keep):
    keep_keys = (key for key in mapping.keys() & keep)
    return ((key, mapping[key]) for key in keep_keys)


def drop_keys(mapping, *, drop):
    keep_keys = (key for key in mapping.keys() - drop)
    return ((key, mapping[key]) for key in keep_keys)


def filter_keys(mapping, *, where):
    return ((key, value) for key, value in mapping.items() if where(key))


def filterfalse_keys(mapping, *, where):
    return ((key, value) for key, value in mapping.items() if not where(key))


def filter_values(mapping, *, where):
    return ((key, value) for key, value in mapping.items() if where(value))


def filterfalse_values(mapping, *, where):
    return ((key, value) for key, value in mapping.items() if not where(value))


def filter_items(mapping, *, where):
    return (
        (key, value)
        for key, value in mapping.items() if where(key, value)
    )


def filterfalse_items(mapping, *, where):
    return (
        (key, value)
        for key, value in mapping.items() if not where(key, value
                                                       ))


def grouped(
    sequence: Sequence[VT],
    *,
    by: Callable[[VT], KT],
    group_factory: Type[Collection] = list,
) -> Iterator[Tuple[KT, MutableSequence[VT]]]:
    for k, items in itertools.groupby(sorted(sequence, key=by), by):
        yield (by, group_factory(items))


def inverted(
        mapping: Mapping[KT, VT]) -> Iterator[Tuple[VT, KT]]:
    return ((v, k) for k, v in mapping.items())


def inverted_last_seen(
        mapping: Mapping[KT, HVT]) -> Iterator[Tuple[HVT, KT]]:
    seen = dict(inverted(mapping))
    return iter(seen.items())


def inverted_first_seen(
        mapping: Mapping[KT, HVT]) -> Iterator[Tuple[HVT, KT]]:
    seen = set()
    saw = seen.add
    for v, k in inverted(mapping):
        if v not in seen:
            saw(v)
            yield (v, k)


def inverted_multi_values(
        mapping: Mapping[KT, HVT],
        *,
        item_factory: Type[Collection],
        record_item: Callable[[Collection, KT], None],
) -> Iterator[Tuple[HVT, KT]]:
    inverted = collections.defaultdict(item_factory)
    for k, v in mapping.items():
        record_item(inverted[v], k)
    return iter(inverted.items())


def inverted_ordered_multi_values(
        mapping: Mapping[KT, HVT]) -> Iterator[Tuple[HVT, KT]]:
    def append_item(key_list: MutableSequence[KT], item: KT) -> None:
        key_list.append(item)
    return inverted_multi_values(
        mapping,
        item_factory=list,
        record_item=append_item,
    )


def inverted_counted_multi_values(
        mapping: Mapping[KT, HVT]) -> Iterator[Tuple[HVT, KT]]:
    def count_item(key_counter: collections.Counter, item: KT):
        key_counter.update(item)
    return inverted_multi_values(
        mapping,
        item_factory=collections.Counter,
        record_item=count_item,
    )


def inverted_unique_multi_values(
        mapping: Mapping[KT, HVT]) -> Iterator[Tuple[HVT, KT]]:
    def add_item(key_set: MutableSet[KT], item: KT):
        key_set.add(item)
    return inverted_multi_values(
        mapping,
        item_factory=set,
        record_item=add_item,
    )


def inner_join(first, *others):
    def inner_joined_items(k):
        yield first[k]
        for other in others:
            other[k]

    keys = set(first.keys()).intersection(*[other.keys() for other in others])
    for k in keys:
        yield (k, tuple(inner_joined_items(k)))


def inner_join2(left, right):
    for k in left.keys() & right.keys():
        yield (k, (left[k], right[k]))


def outer_join(first, *others, default=None):
    def outer_joined_items(k):
        yield first[k]
        for other in others:
            yield other.get(k, default)

    keys = set(first.keys()).union(*[other.keys() for other in others])
    for k in keys:
        yield (k, tuple(outer_joined_items(k)))


def outer_join2(left, right, *, default=None):
    for k in left.keys() | right.keys():
        yield (k, (left.get(k, default), right.get(k, default)))


def left_join(first, *others, default=None):
    def left_joined_items(k):
        yield first[k]
        for other in others:
            yield other.get(k, default)

    for k in first.keys():
        yield (k, tuple(left_joined_items(k)))


def left_join2(left, right, *, default=None):
    for k in left.keys():
        yield (k, (left[k], right.get(k, default)))


def _tupleize_keys(k1, k2) -> Tuple[Hashable, ...]:
    if k1 is None:
        return (k2,)
    else:
        return k1 + (k2,)


def flatten(
        obj: Any,
        *,
        key_reducer: Callable[[Hashable], Hashable] = _tupleize_keys,
        _key=None,
        _memo=None,
) -> Iterator[Tuple[Tuple[Hashable, ...], Any]]:
    if _memo is None:
        _memo = set()
    if litecore.check.is_mapping(obj):
        iterator = obj.items()
    elif litecore.check.is_iterable_but_do_not_recurse(obj):
        iterator = enumerate(obj)
    else:
        iterator = None
    if iterator:
        if id(obj) not in _memo:
            _memo.add(id(obj))
            for k, value in iterator:
                yield from flatten(
                    value,
                    key_reducer=key_reducer,
                    _key=key_reducer(_key, k),
                    _memo=_memo,
                )
            _memo.remove(id(obj))
        # TODO: warn recursive object?
    else:
        yield _key, obj


def modify(
        obj: Any,
        *,
        modify_key: Callable = lambda x: x,
        modify_value: Callable = lambda x, original_key: x,
        mapping_factory: Callable = None,
        iterable_factory: Callable = None,
        _memo=None,
):
    if _memo is None:
        _memo = set()
    if litecore.check.is_mapping(obj):
        _memo.add(id(obj))
        factory = type(obj) if mapping_factory is None else mapping_factory
        new_obj = factory()
        for key, value in obj.items():
            new_obj[modify_key(key)] = modify_value(
                modify(
                    value,
                    modify_key=modify_key,
                    modify_value=modify_value,
                    mapping_factory=mapping_factory,
                    iterable_factory=iterable_factory,
                    _memo=_memo,
                ),
                original_key=key,
            )
        _memo.remove(id(obj))
    elif litecore.check.is_iterable_but_do_not_recurse(obj):
        _memo.add(id(obj))
        factory = type(obj) if iterable_factory is None else iterable_factory
        new_obj = factory(
            modify(
                value,
                modify_key=modify_key,
                modify_value=modify_value,
                mapping_factory=mapping_factory,
                iterable_factory=iterable_factory,
                _memo=_memo,
            ) for value in obj
        )
        _memo.remove(id(obj))
    else:
        return obj
    return new_obj


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
