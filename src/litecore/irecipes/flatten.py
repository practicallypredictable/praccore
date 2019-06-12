"""Functions for flattening iterables at various depth levels.

"""
import collections
import itertools

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
)


def flatten(iterables: Iterable[Iterable[Any]]) -> Iterator[Any]:
    """Flatten an iterable of iterables into one consecutive iterator.

    Only flattens one level of iterables.

    Arguments:
        iterables: iterable of iterable objects with items to be flattened

    Returns:
        iterator of the consecutive items of the underlying iterables

    Examples:

    >>> list(flatten([range(3), [-1], range(3, 6)]))
    [0, 1, 2, -1, 3, 4, 5]
    >>> ' '.join(flatten(['abc', 'def', 'ghi', 'jkl']))
    'a b c d e f g h i j k l'

    """
    return itertools.chain.from_iterable(iterables)


def flatmap(
        func: Callable[[Any], Any],
        iterable: Iterable[Any],
) -> Iterator[Any]:
    """Map a function to items of an iterable and flatten the result.

    Arguments:
        func: single-argument callable to be mapped to items of the iterable
        iterable: iterable object with items to be flattened

    Examples:

    >>> shows = [
    ...     {'id': 1, 'topics': [1, 2, 3]},
    ...     {'id': 2, 'topics': [1, 4, 5]},
    ...     {'id': 3, 'topics': [2, 5, 6]},
    ... ]
    >>> def show_topics(show):
    ...     return [
    ...         {'id': show['id'], 'topic': topic}
    ...         for topic in show['topics']
    ...     ]
    >>> list(flatmap(show_topics, shows))  # doctest: +ELLIPSIS
    [{'id': 1, 'topic': 1}, ..., {'id': 3, 'topic': 5}, {'id': 3, 'topic': 6}]

    """
    return itertools.chain.from_iterable(map(func, iterable))


def deepflatten(
        iterable: Iterable[Any],
        *,
        maxdepth: Optional[int] = None,
        primitives: Optional[Tuple[Type, ...]] = None,
) -> Iterator[Any]:
    """Non-recursively flatten a multi-level iterable into one iterator.

    To avoid hitting the recursion depth limit, ignore_types will always be
    treated to include str and bytes. These will implicitly be added to
    whatever sequence is provided by the caller (including None). See the
    Examples.

    Arguments:
        iterable: iterable object with items to be flattened

    Keyword Arguments:
        maxdepth: limit on number of levels to flatten (optional; default is
            None, signifying no limit to structure depth)
        primitives: tuple of types which will not be flattened (optional;
            default of None signifies str and bytes, which are implicitly
            included in any set of primitives which will not be flattened)

    Yields:
        consecutive items of the flattened iterable

    Examples:

    >>> list(deepflatten([range(2), [range(3), range(4)], range(5)]))
    [0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4]
    >>> list(deepflatten([range(3), 'abc', range(3), 'def']))
    [0, 1, 2, 'abc', 0, 1, 2, 'def']
    >>> from collections import namedtuple
    >>> Record = namedtuple('Record', 'name age address')
    >>> n = Record(name='Joe', age=25, address='123 W. 45th St')
    >>> list(deepflatten(['abc', n, 'def']))
    ['abc', 'Joe', 25, '123 W. 45th St', 'def']
    >>> list(deepflatten(['abc', n, 'def'], primitives=(tuple,)))
    ['abc', Record(name='Joe', age=25, address='123 W. 45th St'), 'def']
    >>> items = [1, [2, (3, 4), {(5, 6): 'abc'}, 7], 8]
    >>> list(deepflatten(items))
    [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(deepflatten(items, primitives=(tuple,)))
    [1, 2, (3, 4), (5, 6), 7, 8]
    >>> list(deepflatten(items, primitives=(tuple, dict)))
    [1, 2, (3, 4), {(5, 6): 'abc'}, 7, 8]
    >>> recursive = list(range(5))
    >>> recursive.append(recursive)
    >>> list(deepflatten(recursive))
    [0, 1, 2, 3, 4, [0, 1, 2, 3, 4, [...]]]

    """
    seen = set()
    saw = seen.add
    stack = collections.deque()
    push_stack = stack.append
    pop_stack = stack.pop
    push_stack(iter(iterable))
    saw(id(iterable))
    while stack:
        iterator = pop_stack()
        while True:
            try:
                item = next(iterator)
            except StopIteration:
                break
            else:
                is_chars = isinstance(item, (str, bytes, bytearray))
                if not is_chars:
                    try:
                        iter(item)
                    except TypeError:
                        is_iterable = False
                    else:
                        is_iterable = True
                if primitives is not None and not is_chars and is_iterable:
                    do_not_iterate = isinstance(item, primitives)
                else:
                    do_not_iterate = is_chars or not is_iterable
                if do_not_iterate or id(item) in seen:
                    yield item
                else:
                    saw(id(item))
                    if maxdepth is None or len(stack) < maxdepth:
                        push_stack(iterator)
                        iterator = iter(item)
                    else:
                        yield item
