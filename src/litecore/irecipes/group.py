"""Functions and classes for grouping and simple run-length encoding.

"""
import collections
import dataclasses
import functools
import itertools
import operator

from typing import (
    Any,
    Container,
    Hashable,
    Iterator,
    Iterable,
    List,
    Optional,
    Tuple,
)

import litecore.irecipes.common as _common

from litecore.irecipes.typealiases import (
    FilterFunc,
    KeyFunc,
    HashableKeyFunc,
    Prioritized,
    Prioritizer,
)


def _contains(value: Any, *, group: Container[Any]) -> Prioritized:
    return (0, value) if value in group else (1, value)


def _predicate_true(value: Any, *, condition: FilterFunc) -> Prioritized:
    return (0, value) if condition(value) else (1, value)


def prioritize_in(group: Container[Any]) -> Prioritizer:
    """Returns a callable that will prioritize items in the specified group.

    The returned callable will, when passed a value, prioritize the value
    if it is in the specified group by returning a tuple with first item 0 (the
    second item will be the value itself). Values not in the specified group
    will be de-prioritized by having the returned tuple have first item 1. A
    sort of the returned tuples will respect the desired priorization.

    Use this rather than the more general prioritize_where() when the desired
    prioritization is based on simple membership of a group. It is likely to be
    faster than prioritize_where() in tight loops, since it only does a test
    for container membership and avoids a function invocation.

    Arguments:
        group: container of the values to be prioritized

    Returns:
        callable that, when passed a value, will return a tuple with 2 items
        prioritizing or de-prioritizing the value

    Examples:

    >>> prioritizer = prioritize_in(set([c for c in 'aeiou']))
    >>> word = 'supercalifragilisticexpialidocious'
    >>> sorted(word, key=prioritizer)  # doctest: +ELLIPSIS
    ['a', 'a', 'a', 'e', 'e', 'i', 'i', 'i', ..., 's', 's', 't', 'x']

    """
    return functools.partial(_contains, group=group)


def prioritize_where(condition: FilterFunc) -> Prioritizer:
    """Returns a callable that will prioritize items if a predicate is True.

    The returned callable will, when passed a value, prioritize the value
    if the specified predicate is True for it, by returning a tuple with first
    item 0 (the second item will be the value itself). Values for which the
    specified predicate is False will be de-prioritized by having the returned
    tuple have first item 1. A sort of the returned tuples will respect the
    desired priorization.

    More general and flexible than prioritize_in(), but requires an extra
    function invocation to test the condition.

    Arguments:
        condition: predicate for which values testing True will be prioritized

    Returns:
        callable that, when passed a value, will return a tuple with 2 items
        prioritizing or de-prioritizing the value

    Examples:

    >>> prioritizer = prioritize_where(lambda c: c in 'aeiou')
    >>> word = 'supercalifragilisticexpialidocious'
    >>> sorted(word, key=prioritizer)  # doctest: +ELLIPSIS
    ['a', 'a', 'a', 'e', 'e', 'i', 'i', 'i', ..., 's', 's', 't', 'x']

    """
    return functools.partial(_predicate_true, condition=condition)


def groupby_unsorted(
        iterable: Iterable[Any],
        *,
        key: Optional[HashableKeyFunc] = None,
) -> Iterator[Tuple[Hashable, List[Any]]]:
    """Return an iterator of grouped items, without requiring a sort before.

    A time-efficient alternative to itertools.groupby() which does not require
    a sort of the items prior to the grouping. Requires the items of the
    iterable to be hashable, or a key function which produces a hashable key
    value for grouping each item.

    For non-hashable items, sort and use the usual itertools.groupby() or the
    groupby_sorted() recipe herein.

    Note this function will consume an entire iterator into a dict of lists,
    so be mindful of memory usage for long iterators. Will not return for an
    infinite iterator.

    Arguments:
        iterable: object containing items to be grouped

    Keyword Arguments:
        key: single-argument callable mapping function returning a hashable key
            (optional; defaults to None, which signifies the items of the
            iterable are processed without modification)

    Returns:
        iterator of tuples containing the hashable key and a list of the items
            grouped under that key, in the order in which both the keys and
            respective items were encountered in the iterable

    Examples:

    >>> word = 'supercalifragilisticexpialidocious'
    >>> is_vowel = lambda c: c.lower() in 'aeiou'
    >>> list(groupby_unsorted(word, key=is_vowel))[0]  # doctest: +ELLIPSIS
    (False, ['s', 'p', 'r', 'c', 'l', 'f', 'r', 'g', 'l', 's', ..., 's'])

    """
    groups = collections.defaultdict(list)
    keyed = _common.keyed_items(iterable, key=key)
    for k, item in keyed:
        groups[k].append(item)
    return groups.items()


def groupby_sorted(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator[Tuple[Any, List[Any]]]:
    """Return an iterator of grouped items after sorting an iterable.

    Wrapper for itertools.groupby() which sorts the iterable first. Adapted
    from the Python standard library itertools recipes. See:
        https://docs.python.org/3/library/itertools.html#itertools.groupby

    For hashable items, consider using the groupby_unsorted() recipe herein.

    Note the sort done by this function will consume an entire iterator into a
    list, which will then be copied (i.e., there will be two lists of similar
    length), so be mindful of memory usage for long iterators. Will not return
    for an infinite iterator.

    Arguments:
        iterable: object containing items to be grouped

    Keyword Arguments:
        key: single-argument callable mapping function returning a hashable key
            (optional; defaults to None, which signifies the items of the
            iterable are processed without modification)

    Returns:
        iterator of tuples containing the hashable key and a list of the items
            grouped under that key, in the order in which both the keys and
            respective items were encountered in the iterable

    Examples:

    >>> word = 'supercalifragilisticexpialidocious'
    >>> is_vowel = lambda c: c.lower() in 'aeiou'
    >>> list(groupby_sorted(word, key=is_vowel))[0]  # doctest: +ELLIPSIS
    (False, ['s', 'p', 'r', 'c', 'l', 'f', 'r', 'g', 'l', 's', ..., 's'])

    """
    groups = []
    append_group = groups.append
    keys = []
    append_key = keys.append
    data = sorted(iterable, key=key)
    for k, g in itertools.groupby(data, key=key):
        append_group(list(g))
        append_key(k)
    return zip(keys, groups)


def unique_just_seen(
        iterable: Iterable[Any],
        *,
        key: Optional[KeyFunc] = None,
) -> Iterator:
    """Return an iterator of the unique contiguous items of an iterable.

    Only remembers the most recent run of items. THe first item in each
    continguous run will be yielded.

    The optional key callable specifies a transformation of the items
    which is used to determine whether contiguous items are equal.

    Will not return if passed an infinite iterator.

    Arguments:
        iterable: iterator or collection of items

    Keyword Arguments:
        key: single-argument callable mapping function
            (optional; defaults to None, which signifies the items of the
            iterable are processed without modification)

    Yields:
        the first item in each contiguous group of the iterable (as transformed
        by the key callable, if applicable), in the order it occurs in the
        iterable

    >>> list(unique_just_seen('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D', 'A', 'B']
    >>> list(unique_just_seen('AbBCcAD', key=str.lower))
    ['A', 'b', 'C', 'A', 'D']

    """
    groups = itertools.groupby(iterable, key)
    get_group = operator.itemgetter(1)
    return map(next, map(get_group, groups))


@dataclasses.dataclass(frozen=True)
class Run:
    """Component class for run-length encoding.

    Holds a value and the number of occurrences of that value for a segment of
    the run-legnth encoding.

    Attributes:
        value: the value
        times: the number of consecutive occurrences of that value

    """
    value: Any
    times: int

    @property
    def expansion(self) -> Iterator[Any]:
        """Return an iterator of the value repeated the number of times."""
        return itertools.repeat(self.value, self.times)


class RunLengths:
    """A simple run-legnth encoding of an iterable.

    Represents an iterable as a sequence of Run objects, each containing a
    value and the number of consecutive occurrences of that value in that
    segment of the encoding.

    Arguments:
        iterable: the object to be run-length encoded

    >>> data = [1, 1, 1, 3, 3, 3, 3, 2, 2, 2]
    >>> runs = RunLengths(data)
    >>> list(runs.encoding)
    [Run(value=1, times=3), Run(value=3, times=4), Run(value=2, times=3)]
    >>> list(runs.expand)
    [1, 1, 1, 3, 3, 3, 3, 2, 2, 2]

    """

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._encoding = [
            Run(value=value, times=len(list(run)))
            for value, run in itertools.groupby(iterable)
        ]

    @property
    def encoding(self) -> Iterator[Run]:
        """Iterator of the run-length encoding segmnents."""
        for run in self._encoding:
            yield run

    @property
    def expand(self) -> Iterator[Any]:
        """Iterator of the values of the original iterable."""
        return itertools.chain.from_iterable(
            run.expansion for run in self.encoding
        )
