"""Functions for flattening iterables at various depth levels.

"""
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

    Only flattens one level (i.e., items which are themselves iterable
    will be unaffected).

    Arguments:
        iterables: iterable of iterables with items to be flattened

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
    """Apply a function to items of an iterable and flatten the result.

    Arguments:
        func: single-argument callable to be applied to each item
        iterable: object with items to be flattened

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
        exclude_types: Optional[Tuple[Type, ...]] = None,
) -> Iterator[Any]:
    """Non-recursively flatten a multi-level iterable into one iterator.

    To avoid hitting the recursion depth limit, ignore_types will always
    implicitly include str, bytes and bytearray.

    Arguments:
        iterable: iterable object with items to be flattened

    Keyword Arguments:
        maxdepth: limit on number of levels to flatten (optional; the
            default is None, signifying no limit to structure depth)
        exclude_types: tuple of types which will be included in results
            unaffected (optional; default is None; implicitly includes
            str, bytes and bytearray)

    Yields:
        consecutive items of the flattened iterable

    Examples:

    >>> list(deepflatten([range(2), [range(3), range(4)], range(5)]))
    [0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4]
    >>> list(deepflatten([range(3), 'abc', range(3), 'def']))
    [0, 1, 2, 'abc', 0, 1, 2, 'def']
    >>> d = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f'}
    >>> d.update({7: d})
    >>> list(deepflatten(d.items()))
    [1, 'a', 2, 'b', 3, 'c', 4, 'd', 5, 'e', 6, 'f', 7, 1, 2, 3, 4, 5, 6, 7]
    >>> from collections import namedtuple
    >>> Record = namedtuple('Record', 'name age address')
    >>> emp = Record(name='Joe', age=25, address='123 W. 45th St')
    >>> list(deepflatten(['abc', emp, 'def']))
    ['abc', 'Joe', 25, '123 W. 45th St', 'def']
    >>> list(deepflatten(['abc', emp, 'def'], exclude_types=(tuple,)))
    ['abc', Record(name='Joe', age=25, address='123 W. 45th St'), 'def']
    >>> mixed = [1, [2, (3, 4), {(5, 6): 'abc'}, 7], 8]
    >>> list(deepflatten(mixed))
    [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(deepflatten(mixed, exclude_types=(tuple,)))
    [1, 2, (3, 4), (5, 6), 7, 8]
    >>> list(deepflatten(mixed, exclude_types=(tuple, dict)))
    [1, 2, (3, 4), {(5, 6): 'abc'}, 7, 8]
    >>> recursive = list(range(5))
    >>> recursive.append(recursive)
    >>> recursive == list(deepflatten(recursive))
    True

    """
    seen = set()
    saw = seen.add
    saw(id(iterable))
    stack = []
    push_stack = stack.append
    pop_stack = stack.pop
    iterator = iter(iterable)
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            if stack:
                iterator = pop_stack()
                continue
            else:
                return
        else:
            deeper = not isinstance(item, (str, bytes, bytearray))
            if deeper and exclude_types is not None:
                deeper = not isinstance(item, exclude_types)
            if deeper and maxdepth is not None:
                deeper = len(stack) < maxdepth
        if not deeper:
            yield item
        else:
            try:
                child_iterator = iter(item)
            except TypeError:
                yield item
            else:
                if id(item) not in seen:
                    try:
                        hash(item)
                    except TypeError:
                        saw(id(item))
                    push_stack(iterator)
                    iterator = child_iterator
                else:
                    yield item


def deepflatten_recursive(
        iterable: Iterable[Any],
        *,
        maxdepth: Optional[int] = None,
        exclude_types: Optional[Tuple[Type, ...]] = None,
        _depth=None,
        _seen=None,
) -> Iterator[Any]:
    """Recursively flatten a multi-level iterable into one iterator.

    To avoid hitting the recursion depth limit, ignore_types will always
    implicitly include str, bytes and bytearray.

    Arguments:
        iterable: iterable object with items to be flattened

    Keyword Arguments:
        maxdepth: limit on number of levels to flatten (optional; the
            default is None, signifying no limit to structure depth)
        exclude_types: tuple of types which will be included in results
            unaffected (optional; default is None; implicitly includes
            str, bytes and bytearray)

    Yields:
        consecutive items of the flattened iterable

    Examples:

    >>> list(deepflatten_recursive([range(2), [range(3), range(4)], range(5)]))
    [0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4]
    >>> list(deepflatten_recursive([range(3), 'abc', range(3), 'def']))
    [0, 1, 2, 'abc', 0, 1, 2, 'def']
    >>> d = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f'}
    >>> d.update({7: d})
    >>> list(deepflatten_recursive(d.items()))
    [1, 'a', 2, 'b', 3, 'c', 4, 'd', 5, 'e', 6, 'f', 7, 1, 2, 3, 4, 5, 6, 7]
    >>> from collections import namedtuple
    >>> Record = namedtuple('Record', 'name age address')
    >>> emp = Record(name='Joe', age=25, address='123 W. 45th St')
    >>> list(deepflatten_recursive(['abc', emp, 'def']))
    ['abc', 'Joe', 25, '123 W. 45th St', 'def']
    >>> list(deepflatten_recursive(['abc', emp, 'def'], exclude_types=(tuple,)))
    ['abc', Record(name='Joe', age=25, address='123 W. 45th St'), 'def']
    >>> mixed = [1, [2, (3, 4), {(5, 6): 'abc'}, 7], 8]
    >>> list(deepflatten_recursive(mixed))
    [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(deepflatten_recursive(mixed, exclude_types=(tuple,)))
    [1, 2, (3, 4), (5, 6), 7, 8]
    >>> list(deepflatten_recursive(mixed, exclude_types=(tuple, dict)))
    [1, 2, (3, 4), {(5, 6): 'abc'}, 7, 8]
    >>> recursive = list(range(5))
    >>> recursive.append(recursive)
    >>> recursive == list(deepflatten_recursive(recursive))
    True

    """
    if _depth is None:
        _depth = 0
    if _seen is None:
        _seen = set()
        _seen.add(id(iterable))
    for item in iterable:
        try:
            iter(item)
        except TypeError:
            deeper = False
        else:
            deeper = not isinstance(item, (str, bytes, bytearray))
            if deeper and exclude_types is not None:
                deeper = not isinstance(item, exclude_types)
            if deeper and maxdepth is not None:
                deeper = _depth < maxdepth
        if deeper and id(item) not in _seen:
            _seen.add(id(item))
            yield from deepflatten_recursive(
                item,
                maxdepth=maxdepth,
                exclude_types=exclude_types,
                _depth=_depth + 1,
                _seen=_seen,
            )
            _seen.remove((id(item)))
        else:
            yield item
