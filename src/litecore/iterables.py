import itertools
import functools
import operator

from typing import (
    Callable,
    Hashable,
    Iterable,
    TypeVar,
)

from .sentinel import NO_VALUE

T = TypeVar('T')


def all_equal(one: Iterable[T], other: Iterable[T]) -> bool:
    try:
        if len(one) != len(other):
            return False
        return all(x == y for x, y in zip(one, other))
    except TypeError:
        for x, y in itertools.zip_longest(one, other, fillvalue=NO_VALUE):
            if NO_VALUE in (x, y) or x != y:
                return False
        return True


def hash_reduce(
        iterable: Iterable[Hashable],
        *,
        operation: Callable[[int, int], int] = operator.xor,
) -> int:
    hashes = map(hash, iterable)
    return functools.reduce(operation, hashes, 0)
