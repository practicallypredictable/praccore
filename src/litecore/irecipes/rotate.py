"""Functions for cycling or rotating items between one or more iterables.

"""
import itertools

from typing import (
    Any,
    Iterable,
    Iterator,
    Optional,
    Tuple,
)

import litecore.irecipes.common as _common


def finite_cycle(times: int, iterable: Iterable[Any]) -> Iterator[Any]:
    """Return iterator cycling through a given iterable finitely-many times.

    The passed iterable is assumed to be finite.

    Arguments:
        times: integral number of times to repeat the iterable
        iterable: finite iterable to be repeated

    Returns:
        iterator repeating the passed iterable the specified number of times

    Examples:

    >>> pattern = 'hee haw'.split()
    >>> list(finite_cycle(3, pattern))
    ['hee', 'haw', 'hee', 'haw', 'hee', 'haw']

    """
    repeated = itertools.repeat(tuple(iterable), times)
    return itertools.chain.from_iterable(repeated)


def enumerate_cycle(
        iterable: Iterable[Any],
        *,
        times: Optional[int] = None,
) -> Iterator[Tuple[int, Any]]:
    """Return iterator of tuples indicating cycle count and item.

    The passed iterable is assumed to be finite.

    Arguments:
        iterable: finite iterable to be repeated

    Keyword Arguments:
        times: integral number of times to repeat the iterable (optional;
            default is None, signifying the cycle should be repeated
            infinitely)

    Returns:
        iterator of tuples consisting of the number of the cycle and each item
        of the passed iterable, repeating the cycle the specified number
        of times (or infinitely, if no number of times is specified)

    Examples:

    >>> pattern = 'hee haw'.split()
    >>> list(enumerate_cycle(pattern, times=3))
    [(0, 'hee'), (0, 'haw'), (1, 'hee'), (1, 'haw'), (2, 'hee'), (2, 'haw')]

    """
    iterable = tuple(iterable)
    if not iterable:
        return iter(())
    counter = itertools.count() if times is None else range(times)
    return ((i, item) for i in counter for item in iterable)


def round_robin_shortest(*iterables) -> Iterator:
    """Return iterator yielding from each iterable in turn.

    Stop when the last item from the shortest iterable is yielded.

    Arguments:
        an arbitrary number of iterable positional arguments

    Returns:
        iterator rotating among iterables until the shortest is exhausted

    Examples:

    >>> numbers = range(3)
    >>> chars = 'abcde'
    >>> classes = [int, str, dict, list]
    >>> list(round_robin_shortest(numbers, chars, classes))
    [0, 'a', <class 'int'>, 1, 'b', <class 'str'>, 2, 'c', <class 'dict'>]

    """
    return itertools.chain.from_iterable(zip(*iterables))


def round_robin(*iterables) -> Iterator:
    """Return iterator yielding from each iterable in turn.

    Continue until all iterables have been consumed. As each iterable is
    consumed, it falls out of the rotation.

    Same as the standard library itertools recipe roundrobin(). See:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Arguments:
        an arbitrary number of iterable positional arguments

    Returns:
        iterator rotating among iterable arguments until all are exhausted

    Examples:

    >>> numbers = range(3)
    >>> chars = 'abcde'
    >>> classes = [int, str, dict, list]
    >>> list(round_robin(numbers, chars, classes))  # doctest: +ELLIPSIS
    [0, 'a', ... 2, 'c', <class 'dict'>, 'd', <class 'list'>, 'e']

    """
    active = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while active:
        try:
            for get_next in nexts:
                yield get_next()
        except StopIteration:
            active -= 1
            nexts = itertools.cycle(itertools.islice(nexts, active))


def rotate_cycle(iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
    """Return infinite iterator rotating through given values.

    Items of the returned iterator will all be tuples of the same length as the
    passed iterable (which must be finite). The items of each tuple will be
    rotated one position relative to the preceding tuple. The first tuple will
    have the items in the same order as the passed iterable.

    The rotating pattern will cycle endlessly.

    If the iterable is an iterator, it will be consumed.

    Arguments:
        iterable: finite iterable specifying values to be cycled

    Returns:
        infinite iterator cycling through the given values

    >>> from litecore.irecipes.common import take
    >>> take(5, rotate_cycle(range(4)))
    [(0, 1, 2, 3), (1, 2, 3, 0), (2, 3, 0, 1), (3, 0, 1, 2), (0, 1, 2, 3)]

    """
    items = tuple(iterable)
    return _common.window(len(items), itertools.cycle(items))


def intersperse(
        value: Any,
        iterable: Iterable[Any],
        *,
        spacing: int = 1,
) -> Iterator:
    """Introduce a value between items of an iterable.

    The default behavior is to introduce the value between every item of the
    iterable. This can be altered by providing the spacing keyword argument.

    The iterator's last item will be the last item of the original iterable.

    Arguments:
        value: the value to introduced
        iterable: collection or iterator of items

    Keyword Arguments:
        spacing: positive number of items from the original iterable between
            each instance of the introduced value

    Returns:
        iterator with the value introduced between items of original iterable

    Raises:
        ValueError: if spacing argument is less than 1

    >>> list(intersperse('hi', range(5)))
    [0, 'hi', 1, 'hi', 2, 'hi', 3, 'hi', 4]
    >>> list(intersperse('hi', range(5), spacing=2))
    [0, 1, 'hi', 2, 3, 'hi', 4]
    >>> list(intersperse('hi', range(4), spacing=2))
    [0, 1, 'hi', 2, 3]

    """
    if spacing == 1:
        filler = itertools.repeat(value)
        return _common.drop(1, round_robin_shortest(filler, iterable))
    elif spacing > 1:
        filler = itertools.repeat([value])
        batches = _common.take_batches(iterable, length=spacing)
        chain = _common.drop(1, round_robin_shortest(filler, batches))
        return itertools.chain.from_iterable(chain)
    else:
        msg = f'spacing argument must be positive'
        raise ValueError(msg)
