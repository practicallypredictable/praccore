"""Convenience functions for mappings.

Unless noted otherwise, each function returns an iterator of (key, value)
tuples in the same order as iteration over the keys of the original mapping
argument. These tuples may then be used to instantiate whatever type of mapping
the user desires.

"""
__all__ = [
    'is_one_to_one',
    'keeping_keys',
    'dropping_keys',
    'keeping_values',
    'dropping_values',
    'inverted',
]

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
)

KT = TypeVar('KT')
VT = TypeVar('VT')


def is_one_to_one(mapping: Mapping[KT, VT]) -> bool:
    """Returns True if a mapping has unique values.

    Python mappings have unique keys, so a mapping is one-to-one if the values
    are unique.

    >>> is_one_to_one({'a': 1, 'b': 2, 'c': 3})
    True
    >>> is_one_to_one({'a': 1, 'b': 2, 'c': 2})
    False

    """
    return len(set(mapping.values())) == len(mapping.values())


def _meets_condition(
        *,
        iterable: Optional[Iterable[Any]] = None,
        callable: Optional[Callable[[Any], bool]] = None,
) -> Callable[[Any], bool]:
    identified = set(iterable) if iterable is not None else set()

    def inner_func(x: Any) -> bool:
        meets = False
        if x in identified:
            meets = True
        if callable is not None and callable(x):
            meets = True
        return meets

    return inner_func


def keeping_keys(
        mapping: Mapping[KT, VT],
        *,
        keys: Optional[Iterable[KT]] = None,
        where: Optional[Callable[[KT], bool]] = None,
) -> Iterator[Tuple[KT, VT]]:
    """Return mapping keeping items with keys matching conditions.

    Args:
        mapping: the mapping to be filtered
        keys (optional): iterable of keys to be kept
        where (optional): callable returning True for keys to keep
    Returns:
        new mapping of same type as original mapping with only kept keys

    If keys argument is not None, any keys in the mapping that appear in the
    keys argument will be kept.

    If where argument is not None, any key for which where(key) is True will
    be kept.

    If both arguments are not None, a key either in keys or for which where is
    True will be kept.

    >>> data = {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(keeping_keys(data))
    {}
    >>> dict(keeping_keys(data, keys=data.keys()))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(keeping_keys(data, keys=['b', 'e']))
    {'b': 3, 'e': 4}
    >>> dict(keeping_keys(data, where=lambda x: x.lower() in 'aeiou'))
    {'a': 1, 'A': 2, 'e': 4, 'i': 5}
    >>> dict(keeping_keys(data, where=lambda x: x.lower() in 'aeiou', keys=['b']))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}

    """
    keep = _meets_condition(iterable=keys, callable=where)
    for k, v in mapping.items():
        if keep(k):
            yield (k, v)


def dropping_keys(
        mapping: Mapping[KT, VT],
        *,
        keys: Optional[Iterable[KT]] = None,
        where: Optional[Callable[[KT], bool]] = None,
) -> Iterator[Tuple[KT, VT]]:
    """Return mapping dropping items with keys matching conditions.

    Args:
        mapping: the mapping to be filtered
        keys (optional): iterable of keys to be dropped
        where (optional): callable returning True for keys to drop
    Returns:
        new mapping of same type as original mapping without dropped keys

    If keys argument is not None, any keys in the mapping that appear in the
    keys argument will be dropped.

    If where argument is not None, any key for which where(key) is True will
    be dropped.

    If both arguments are not None, a key either in keys or for which where is
    True will be dropped.

    >>> data = {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(dropping_keys(data))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(dropping_keys(data, keys=data.keys()))
    {}
    >>> dict(dropping_keys(data, keys=['b', 'e']))
    {'a': 1, 'A': 2, 'i': 5}
    >>> dict(dropping_keys(data, where=lambda x: x.lower() in 'aeiou'))
    {'b': 3}
    >>> dict(dropping_keys(data, where=lambda x: x.lower() in 'b', keys=['e', 'i']))
    {'a': 1, 'A': 2}

    """
    drop = _meets_condition(iterable=keys, callable=where)
    for k, v in mapping.items():
        if not drop(k):
            yield (k, v)


def keeping_values(
        mapping: Mapping[KT, VT],
        *,
        values: Optional[Iterable[VT]] = None,
        where: Optional[Callable[[VT], bool]] = None,
) -> Iterator[Tuple[KT, VT]]:
    """Return mapping keeping items with values matching conditions.

    Args:
        mapping: the mapping to be filtered
        values (optional): iterable of values to be kept
        where (optional): callable returning True for values to keep
    Returns:
        new mapping of same type as original mapping with only kept values

    If values argument is not None, any values in the mapping that appear in the
    values argument will be kept.

    If where argument is not None, any value for which where(value) is True will
    be kept.

    If both arguments are not None, a value either in values or for which where is
    True will be kept.

    >>> data = {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(keeping_values(data))
    {}
    >>> dict(keeping_values(data, values=data.values()))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(keeping_values(data, values=[3, 4]))
    {'b': 3, 'e': 4}
    >>> dict(keeping_values(data, where=lambda x: x != 3))
    {'a': 1, 'A': 2, 'e': 4, 'i': 5}
    >>> dict(keeping_values(data, where=lambda x: x != 2, values=[2]))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}

    """
    keep = _meets_condition(iterable=values, callable=where)
    for k, v in mapping.items():
        if keep(v):
            yield (k, v)


def dropping_values(
        mapping: Mapping[KT, VT],
        *,
        values: Optional[Iterable[VT]] = None,
        where: Optional[Callable[[VT], bool]] = None,
) -> Iterator[Tuple[KT, VT]]:
    """Return mapping dropping items with values matching conditions.

    Args:
        mapping: the mapping to be filtered
        values (optional): iterable of values to be dropped
        where (optional): callable returning True for values to drop
    Returns:
        new mapping of same type as original mapping without dropped values

    If values argument is not None, any values in the mapping that appear in the
    values argument will be dropped.

    If where argument is not None, any value for which where(value) is True will
    be dropped.

    If both arguments are not None, a value either in values or for which where is
    True will be dropped.

    >>> data = {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(dropping_values(data))
    {'a': 1, 'A': 2, 'b': 3, 'e': 4, 'i': 5}
    >>> dict(dropping_values(data, values=data.values()))
    {}
    >>> dict(dropping_values(data, values=[3, 4]))
    {'a': 1, 'A': 2, 'i': 5}
    >>> dict(dropping_values(data, where=lambda x: x != 3))
    {'b': 3}
    >>> dict(dropping_values(data, where=lambda x: x >= 4, values=[3]))
    {'a': 1, 'A': 2}

    """
    drop = _meets_condition(iterable=values, callable=where)
    for k, v in mapping.items():
        if not drop(v):
            yield (k, v)


def inverted(mapping: Mapping[KT, VT]) -> Iterator[Tuple[KT, VT]]:
    """Returns a mapping inverting the values and keys of a given mapping.

    Args:
        mapping: the mapping to be inverted
    Returns:
        inverted mapping, potentially sorted and with computed keys

    The keys of the returned mapping will be based upon the values of the
    original mapping. The values of the returned mapping will be the keys of
    the orignal mapping.

    If the original mapping is not 1-to-1 (i.e., there are duplicate values),
    the last observed item iterating through the original mapping's keys will
    be the only item retained in the returned mapping.

    >>> original = {'a': 2, 'b': -1, 'c': 0, 'd': -3}
    >>> dict(inverted(original))
    {2: 'a', -1: 'b', 0: 'c', -3: 'd'}
    >>> one_to_many = {'alice': 10, 'bob': 20, 'charlie': 10, 'david': 20}
    >>> dict(inverted(one_to_many))
    {10: 'charlie', 20: 'david'}

    """
    for k, v in mapping.items():
        yield (v, k)
