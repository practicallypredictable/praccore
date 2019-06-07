"""Various functions which process one or more iterables.

Many functions/generators yield items from or return a modified iterator.

"""
import itertools

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Union,
)

import litecore.utils
from litecore.sentinels import NO_VALUE as _NO_VALUE
import litecore.irecipes.common as _common
from litecore.irecipes.typealiases import FilterFunc, KeyFunc


def prepend(
        iterable: Iterable[Any],
        value: Any,
        *,
        times: int = 1,
) -> Iterator:
    """Return an iterator with a specified value prepended.

    Arguments:
        iterable: the iterable to which the value is to be prepended
        value: the value to prepend to the iterable

    Keyword Arguments:
        times: number of times to prepend the value (optional; default is 1)

    Returns:
        iterable combining the prepended value and the original iterable

    Examples:

    >>> list(prepend(range(5), -1))
    [-1, 0, 1, 2, 3, 4]
    >>> list(prepend(['off to work we go'], 'hi ho', times=2))
    ['hi ho', 'hi ho', 'off to work we go']

    """
    return itertools.chain([value] * times, iterable)


def pad(
        iterable: Iterable[Any],
        value: Any,
        *,
        times: Optional[int] = None,
) -> Iterator:
    """Return iterator of original iterable followed by specified padding.

    Default behavior is to add an infinite number of None objects on the end
    of the provided iterable; however both the object to be added and the
    number of times can be modified by the keyword arguments.

    Arguments:
        iterable: object to be padded
        value: object to be added at the end

    Keyword Arguments:
        times: number of times to pad (optional; default is None)

    Examples:

    >>> list(pad(range(5), None, times=3))
    [0, 1, 2, 3, 4, None, None, None]
    >>> list(pad(['baby shark'], 'do', times=6))
    ['baby shark', 'do', 'do', 'do', 'do', 'do', 'do']

    """
    return itertools.chain(iterable, itertools.repeat(value, times=times))


def partition(
        iterable: Iterable[Any],
        *,
        by: Callable[[Any], bool],
) -> Tuple[Iterator, Iterator]:
    """Split an iterable into two iterators based upon a condition.

    Returns two iteators, one for which the condition is False, and one for
    which the condition is True.

    The condition is specified by the required keyword argument by, which just
    be a callable returning True or False based upon the value of one argument.
    It will be called for each item in the iterable in sequence.

    Arguments:
        iterable: object for which items are to be partitioned

    Keyword Arguments:
        by: callable which takes one argument and returns a bool

    Returns:
        a tuple of two iterators, the first of which iterates over all items of
        the original iterable for which the condition is False, and the other
        for which the condition is True

    Examples:

    >>> odd, even = partition(range(10), by=lambda n: n % 2 == 0)
    >>> list(odd)
    [1, 3, 5, 7, 9]
    >>> list(even)
    [0, 2, 4, 6, 8]
    >>> text = 'We hold these truths to be self-evident'.split()
    >>> short, long = partition(text, by=lambda s: len(s) > 4)
    >>> list(short)
    ['We', 'hold', 'to', 'be']
    >>> list(long)
    ['these', 'truths', 'self-evident']

    """
    false_it, true_it = itertools.tee(iterable)
    return (itertools.filterfalse(by, false_it), filter(by, true_it))


def split(
        iterable: Iterable[Any],
        *,
        at: int,
):
    first, second = itertools.tee(iterable)
    return itertools.islice(first, at), itertools.islice(second, at, None)


def take_then_split(
        iterable: Iterable[Any],
        *,
        until: Callable,
):
    first, second = itertools.tee(iterable)
    return itertools.takewhile(until, first), itertools.dropwhile(until, second)


def split_after(
        iterable: Iterable[Any],
        *,
        each_time: Callable,
):
    cache = []
    for item in iterable:
        cache.append(item)
        if each_time(item) and cache:
            yield cache
            cache = []
    if cache:
        yield cache


def split_before(iterable, *, each_time: Callable):
    cache = []
    for item in iterable:
        if each_time(item) and cache:
            yield cache
            cache = []
        cache.append(item)
    yield cache


def replace(
        iterable: Iterable[Any],
        condition: Union[FilterFunc, Any],
        new_value: Union[KeyFunc, Any],
        *,
        maxreplacements: Optional[int] = None,
) -> Iterator[Any]:
    """Replace specified values of an iterable.

    Returns an iterator of items from an iterable, replacing any values which
    match a condition with a replacement value.

    The condition can either be a value or a single-argument callable. If it is
    a callable, a "truthy" return vlaue for an item passed as an argument means
    that the item should be replaced.

    If the condition is a value, any item matching that value will be replaced.

    The new value can either be a value or a single-argument callable. If it is
    a callable, an item matching the condition will be replaced with the return
    value of the callable passed that item.

    If the new value is an iterable, it will not be flattened/expanded, but
    rather will be included in the returned iterator as-is.

    A limit on the number of replacements may be provided via the keyword
    argument maxreplacements. After hitting any replacement limit, the original
    items of the iterable will be passed through unmodified even if they
    meet the condition for replacement.

    Arguments:
        iterable: object with items to be replaced
        condition: either a value or a single-argument callable
        new_value: either a value or a single-argument callable

    Keyword Arguments:
        maxreplacements: limit on the number of replacements (optional; default
            is None signifying no limit); if provided, must be positive

    Returns:
        iterator of items of the original iterable with the items matching
        the condition replaced

    Raises:
        ValueError: if passed a non-positive maxreplacements argument

    Examples:

    >>> from litecore.irecipes.rotate import finite_cycle
    >>> data = list(finite_cycle(3, [0, 1, 2, 5]))
    >>> list(replace(data, 2, 3))
    [0, 1, 3, 5, 0, 1, 3, 5, 0, 1, 3, 5]
    >>> list(replace(data, 2, [3, 4]))
    [0, 1, [3, 4], 5, 0, 1, [3, 4], 5, 0, 1, [3, 4], 5]
    >>> replace_with = lambda x: str(x)
    >>> list(replace(data, 2, replace_with))
    [0, 1, '2', 5, 0, 1, '2', 5, 0, 1, '2', 5]
    >>> list(replace(data, 2, replace_with, maxreplacements=2))
    [0, 1, '2', 5, 0, 1, '2', 5, 0, 1, 2, 5]
    >>> word = 'anti-establishment'
    >>> is_vowel = lambda s: s.lower() in 'aeiou'
    >>> uppercase = lambda s: s.upper()
    >>> ''.join(replace(word, is_vowel, uppercase))
    'AntI-EstAblIshmEnt'
    >>> list(replace((), 1, 2))
    []

    """
    flagged = _common.flag_where(condition, iterable, maxflags=maxreplacements)
    if callable(new_value):
        return (new_value(item) if flag else item for flag, item in flagged)
    else:
        return (new_value if flag else item for flag, item in flagged)


def replace_multi(
        iterable: Iterable[Any],
        condition: Union[FilterFunc, Any],
        new_value: Union[KeyFunc, Any],
        *,
        items: Optional[int] = None,
        maxreplacements: Optional[int] = None,
) -> Iterator[Any]:
    """Replace specified multiple-item values of an iterable.

    This is an augmented version of replace() above to handle
    multi-item patterns or replacement values. Most of the arguments have the
    same meaning as for replace().

    One difference is the items keyword argument. It must be provided if the
    condition is a callable, since the function needs to know the window size
    to send items to the callable.

    If the condition is a container of values, items is optional since it can
    be inferred from the length of the container. However, if it is provided,
    it must be consistent or an error is raised.

    Another difference is that if the new value is a callable, it must return
    an iterable.

    Arguments:
        iterable: object with items to be replaced
        condition: either a value or a single-argument callable
        new_value: either a value or a single-argument callable

    Keyword Arguments:
        items: length of window of contingous items to examine for a match
            (optional; default is None)
        maxreplacements: limit on the number of replacements (optional; default
            is None signifying no limit); if provided, must be positive

    Returns:
        iterator of items of the original iterable with the items matching
        the condition replaced

    Raises:
        ValueError: if passed a non-positive maxreplacements argument, or
            items is provided and is incorrect, or if items it not provided
            and it must be provided

    Examples:

    >>> from litecore.irecipes.rotate import finite_cycle
    >>> data = list(finite_cycle(3, [0, 1, 2, 5]))
    >>> list(replace_multi(data, [1, 2], [3, 4]))
    [0, 3, 4, 5, 0, 3, 4, 5, 0, 3, 4, 5]
    >>> list(replace_multi(data, [1, 2], [3, 4], maxreplacements=2))
    [0, 3, 4, 5, 0, 3, 4, 5, 0, 1, 2, 5]
    >>> filter_sum_3 = lambda a, b: a + b == 3
    >>> list(replace_multi(data, filter_sum_3, 'hi', items=2))
    [0, 'hi', 5, 0, 'hi', 5, 0, 'hi', 5]
    >>> replace_with = lambda a, b: (a * 10 + b,)
    >>> list(replace_multi(data, filter_sum_3, replace_with, items=2))
    [0, 12, 5, 0, 12, 5, 0, 12, 5]
    >>> list(replace_multi(data, filter_sum_3, -1, items=2, maxreplacements=2))
    [0, -1, 5, 0, -1, 5, 0, 1, 2, 5]
    >>> list(replace_multi((), filter_sum_3, -1, items=2))
    []
    >>> list(replace_multi((0, 1), filter_sum_3, -1, items=2))
    [0, 1]
    >>> list(replace_multi((1, 2), filter_sum_3, -1, items=2))
    [-1]

    """
    if callable(condition):
        if items is None:
            msg = f'must provide number of items if the condition is callable'
            raise ValueError(msg)
        elif items < 1:
            msg = f'number of items must be positive'
            raise ValueError(msg)

        def matches(values):
            try:
                return condition(*values)
            except TypeError:
                return False
    else:
        if items is not None and items != len(condition):
            msg = f'number of items is inconsistent with values to replace'
            raise ValueError(msg)
        else:
            try:
                items = len(condition)
            except TypeError as err:
                msg = f'condition {condition!r} is not a container'
                raise TypeError(msg) from err

        def matches(values):
            return tuple(values) == tuple(condition)
    if callable(new_value):
        def replace_with(values):
            return new_value(*values)
    else:
        if litecore.utils.is_chars(new_value):
            replacement = (new_value,)
        else:
            try:
                replacement = tuple(new_value)
            except TypeError:
                replacement = (new_value,)

        def replace_with(values):
            return replacement
    windows = _common.window(items, pad(iterable, _NO_VALUE, times=items - 1))
    replacements = 0
    for values in windows:
        if matches(values):
            if maxreplacements is None or replacements < maxreplacements:
                replacements += 1
                yield from replace_with(values)
                _common.consume(windows, items=items - 1)
                continue
        if values and values[0] is not _NO_VALUE:
            yield values[0]
