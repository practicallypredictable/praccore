"""Functions for joins between mappings on keys.

"""
from typing import (
    Any,
    Hashable,
    Iterator,
    Mapping,
    Tuple,
    TypeVar,
)

KT = TypeVar('KT', int, str, Hashable)


def inner_join(
        first: Mapping[KT, Any],
        *others,
) -> Iterator[Tuple[KT, Iterator[Any]]]:
    """

    Examples:

    >>> names = {1: 'Alice', 2: 'Bob', 3: 'Charlie', 4: 'Dierdre'}
    >>> salary = {1: 100_000, 2: 90_000, 3: 45_000, 4: 60_000}
    >>> title = {1: 'CEO', 2: 'CFO', 3: 'VP', 4: 'CTO'}
    >>> employees = list(inner_join(names, title, salary))
    >>> employees[0]
    (1, 'Alice', 'CEO', 100000)
    >>> employees[3]
    (4, 'Dierdre', 'CTO', 60000)

    """
    keys = set(first.keys()).intersection(*[m.keys() for m in others])
    for key in keys:
        yield (key, first[key], *[other[key] for other in others])


def inner_join2(
        left: Mapping[KT, Any],
        right: Mapping[KT, Any],
) -> Iterator[Tuple[KT, Tuple[Any, Any]]]:
    for key in left.keys() & right.keys():
        yield (key, left[key], right[key])


def outer_join(
        first: Mapping[KT, Any],
        *others,
        default: Any = None,
) -> Iterator[Tuple[KT, Tuple[Any, ...]]]:
    """

    Examples:

    >>> names = {1: 'Alice', 2: 'Bob', 3: 'Charlie', 4: 'Dierdre'}
    >>> salary = {1: 100_000, 2: 90_000, 3: 45_000, 4: 60_000}
    >>> title = {1: 'CEO', 2: 'CFO', 4: 'CTO'}
    >>> awards = {4: 'employee of the month'}
    >>> promotion = {3: True}
    >>> employees = list(outer_join(title, awards, promotion))
    >>> employees[0]
    (1, 'CEO', None, None)
    >>> employees[2]
    (3, None, None, True)
    >>> employees[3]
    (4, 'CTO', 'employee of the month', None)

    """
    keys = set(first.keys()).union(*[m.keys() for m in others])
    getters = [m.get for m in (first, *others)]
    for key in keys:
        yield (key, *[get(key, default) for get in getters])


def outer_join2(
        left: Mapping[KT, Any],
        right: Mapping[KT, Any],
        *,
        default: Any = None,
) -> Iterator[Tuple[KT, Tuple[Any, Any]]]:
    get_left = left.get
    get_right = right.get
    for key in left.keys() | right.keys():
        yield (key, get_left(key, default), get_right(key, default))


def left_join(
        first: Mapping[KT, Any],
        *others,
        default: Any = None,
) -> Iterator[Tuple[KT, Tuple[Any, ...]]]:
    """

    Examples:

    >>> names = {1: 'Alice', 2: 'Bob', 3: 'Charlie', 4: 'Dierdre'}
    >>> salary = {1: 100_000, 2: 90_000, 3: 45_000, 4: 60_000}
    >>> title = {1: 'CEO', 2: 'CFO', 3: 'VP', 4: 'CTO'}
    >>> awards = {4: 'employee of the month'}
    >>> promotion = {3: True}
    >>> employees = list(left_join(names, title, awards, promotion))
    >>> employees[1]
    (2, 'Bob', 'CFO', None, None)
    >>> employees[2]
    (3, 'Charlie', 'VP', None, True)
    >>> employees[3]
    (4, 'Dierdre', 'CTO', 'employee of the month', None)

    """
    getters = [m.get for m in others]
    for key, first_value in first.items():
        yield (key, first_value, *[get(key, default) for get in getters])


def left_join2(
        left: Mapping[KT, Any],
        right: Mapping[KT, Any],
        *,
        default: Any = None,
) -> Iterator[Tuple[KT, Tuple[Any, Any]]]:
    get_right = right.get
    for key, left_value in left.items():
        yield (key, left_value, get_right(key, default))
