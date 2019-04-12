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
    Callable,
    Collection,
    Iterator,
    Mapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Tuple,
    Type,
)

from litecore._types import KT, VT, HVT


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
        mapping: Mapping[Tuple[KT, VT]]) -> Iterator[Tuple[VT, KT]]:
    return ((v, k) for k, v in mapping.items())


def inverted_last_seen(
        mapping: Mapping[Tuple[KT, HVT]]) -> Iterator[Tuple[HVT, KT]]:
    seen = dict(inverted(mapping))
    return iter(seen.items())


def inverted_first_seen(
        mapping: Mapping[Tuple[KT, HVT]]) -> Iterator[Tuple[HVT, KT]]:
    seen = set()
    saw = seen.add
    for v, k in inverted(mapping):
        if v not in seen:
            saw(v)
            yield (v, k)


def inverted_multi_values(
        mapping: Mapping[Tuple[KT, HVT]],
        *,
        item_factory: Type[Collection],
        record_item: Callable[[Collection, KT], None],
) -> Iterator[Tuple[HVT, KT]]:
    inverted = collections.defaultdict(item_factory)
    for k, v in mapping.items():
        record_item(inverted[v], k)
    return iter(inverted.items())


def inverted_ordered_multi_values(
        mapping: Mapping[Tuple[KT, HVT]]) -> Iterator[Tuple[HVT, KT]]:
    def append_item(key_list: MutableSequence[KT], item: KT) -> None:
        key_list.append(item)
    return inverted_multi_values(
        mapping,
        item_factory=list,
        record_item=append_item,
    )


def inverted_counted_multi_values(
        mapping: Mapping[Tuple[KT, HVT]]) -> Iterator[Tuple[HVT, KT]]:
    def count_item(key_counter: collections.Counter, item: KT):
        key_counter.update(item)
    return inverted_multi_values(
        mapping,
        item_factory=collections.Counter,
        record_item=count_item,
    )


def inverted_unique_multi_values(
        mapping: Mapping[Tuple[KT, HVT]]) -> Iterator[Tuple[HVT, KT]]:
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
