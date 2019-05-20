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

import litecore.utils


def flatten(iterables: Iterable[Iterable[Any]]) -> Iterator[Any]:
    """Flatten an iterable of iterables into one consecutive iterator.

    Does not recurse into deeper-level iterables.

    Arguments:
        iterables: iterable of iterables

    Returns:
        Iterator of the consecutive items of the underlying iterables.

    Examples:

    >>> list(flatten([range(3), [-1], range(3, 6)]))
    [0, 1, 2, -1, 3, 4, 5]
    >>> ' '.join(flatten(['abc', 'def', 'ghi', 'jkl']))
    'a b c d e f g h i j k l'

    """
    return itertools.chain.from_iterable(iterables)


def flatten_map(
        func: Callable[[Any], Any],
        iterable: Iterable[Any],
) -> Iterator[Any]:
    return itertools.chain.from_iterable(map(func, iterable))


def flatten_deep(
        iterable: Iterable[Any],
        *,
        maxlevels: Optional[int] = None,
        primitives: Optional[Tuple[Type, ...]] = None,
        _is_iterable=litecore.utils.is_iterable,
        _is_chars=litecore.utils.is_chars,
) -> Iterator[Any]:
    """Non-recursively flatten a multi-level iterable into one iterator.

    To avoid hitting the recursion depth limit, ignore_types will always be
    treated to include str and bytes. These will implicitly be added to
    whatever sequence is provided by the caller (including None). See the
    Examples.

    Arguments:
        items: iterable of items to be flattened

    Keyword Arguments:
        primitives: tuple of types which will not be recursed into;
            implicitly includes str and bytes, which is also the default

    Returns:
        Iterator of the consecutive items of the underlying iterables.

    Examples:

    >>> list(flatten_deep([range(2), [range(3), range(4)], range(5)]))
    [0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4]
    >>> list(flatten_deep([range(3), 'abc', range(3), 'def']))
    [0, 1, 2, 'abc', 0, 1, 2, 'def']
    >>> from collections import namedtuple
    >>> Record = namedtuple('Record', 'name age address')
    >>> n = Record(name='Joe', age=25, address='123 W. 45th St')
    >>> list(flatten_deep(['abc', n, 'def']))
    ['abc', 'Joe', 25, '123 W. 45th St', 'def']
    >>> list(flatten_deep(['abc', n, 'def'], primitives=(tuple,)))
    ['abc', Record(name='Joe', age=25, address='123 W. 45th St'), 'def']
    >>> items = [1, [2, (3, 4), {(5, 6): 'abc'}, 7], 8]
    >>> list(flatten_deep(items))
    [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(flatten_deep(items, primitives=(tuple,)))
    [1, 2, (3, 4), (5, 6), 7, 8]
    >>> list(flatten_deep(items, primitives=(tuple, dict)))
    [1, 2, (3, 4), {(5, 6): 'abc'}, 7, 8]
    >>> recursive = list(range(5))
    >>> recursive.append(recursive)
    >>> list(flatten_deep(recursive))
    [0, 1, 2, 3, 4, [0, 1, 2, 3, 4, [...]]]

    """
    stack = []
    push = stack.append
    pop = stack.pop
    seen = set()
    saw = seen.add
    push(iter(iterable))
    saw(id(iterable))
    while stack:
        iterator = pop()
        while True:
            try:
                item = next(iterator)
            except StopIteration:
                break
            else:
                do_not_iterate = _is_chars(item) or not _is_iterable(item)
                if not do_not_iterate and primitives is not None:
                    do_not_iterate = isinstance(item, primitives)
                if do_not_iterate or id(item) in seen:
                    yield item
                else:
                    saw(id(item))
                    if maxlevels is None or len(stack) < maxlevels:
                        push(iterator)
                        iterator = iter(item)
                    else:
                        yield item
