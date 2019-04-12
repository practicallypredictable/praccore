import itertools
import logging
import random

from typing import (
    Any,
    Iterable,
    Iterator,
    Optional,
    Tuple,
)

import litecore.mappings

log = logging.getLogger(__name__)


class MultiSet(litecore.mappings.OrderedCounter):
    pass


def power_set(iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
    """

    >>> list(power_set(range(3)))
    [(), (0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)]

    """
    items = list(iterable)
    combos = (itertools.combinations(items, n) for n in range(len(items) + 1))
    return itertools.chain.from_iterable(combos)


def distinct_multisets(
        iterable: Iterable[Any],
        *,
        items: int,
) -> Iterator[Tuple[Any, ...]]:
    """

    >>> import pprint as pp
    >>> pp.pprint(list(distinct_multisets('ABC', items=2)))
    [MultiSet(OrderedDict([('A', 2)])),
     MultiSet(OrderedDict([('A', 1), ('B', 1)])),
     MultiSet(OrderedDict([('A', 1), ('C', 1)])),
     MultiSet(OrderedDict([('B', 2)])),
     MultiSet(OrderedDict([('B', 1), ('C', 1)])),
     MultiSet(OrderedDict([('C', 2)]))]

    """
    combos = itertools.combinations_with_replacement(iterable, items)
    return map(MultiSet, combos)


def random_product(
        *iterables,
        repeat: int = 1,
        rng: Optional[random.Random] = None,
):
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> suits = 'CDHS'
    >>> ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
    >>> card = random_product(ranks, suits, rng=random)
    >>> card
    (4, 'C')
    >>> random_product(ranks, suits, repeat=5, rng=random)
    (6, 'C', 9, 'S', 9, 'S', 'A', 'D', 3, 'S')

    """
    choice = random.choice if rng is None else rng.choice
    space = [tuple(value) for value in iterables] * repeat
    return tuple(choice(item) for item in space)


def random_permutation(
        iterable,
        *,
        items: Optional[int] = None,
        rng: Optional[random.Random] = None,
):
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> suits = 'CDHS'
    >>> ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
    >>> import itertools
    >>> def make_deck(): return itertools.product(ranks, suits)
    >>> len(list(make_deck()))
    52
    >>> hand = random_permutation(make_deck(), items=5, rng=random)
    >>> hand
    ((4, 'C'), ('J', 'C'), ('A', 'S'), ('A', 'C'), (3, 'C'))
    >>> shuffled_deck = random_permutation(make_deck(), rng=random)
    >>> len(list(shuffled_deck))
    52
    >>> shuffled_deck[:5]
    ((6, 'C'), (3, 'S'), (9, 'S'), ('A', 'C'), (9, 'C'))

    """
    sample = random.sample if rng is None else rng.sample
    space = tuple(iterable)
    items = len(space) if items is None else items
    return tuple(sample(space, items))


def random_combination(
        iterable,
        *,
        items: int,
        rng: Optional[random.Random] = None,
):
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> wallet = [1] * 5 + [5] * 2 + [10] * 5 + [20] * 3
    >>> random_combination(wallet, items=3, rng=random)
    (1, 10, 20)

    """
    sample = random.sample if rng is None else rng.sample
    space = tuple(iterable)
    n = len(space)
    indices = sorted(sample(range(n), items))
    return tuple(space[i] for i in indices)


def random_combination_with_replacement(
        iterable,
        *,
        items: int,
        rng: Optional[random.Random] = None,
):
    """

    >>> from random import Random
    >>> random = Random(1)
    >>> wallet = [1] * 5 + [5] * 2 + [10] * 5 + [20] * 3
    >>> random_combination_with_replacement(wallet, items=3, rng=random)
    (1, 10, 20)

    """
    randrange = random.sample if rng is None else rng.sample
    space = tuple(iterable)
    n = len(space)
    indices = sorted(randrange(range(n), items))
    return tuple(space[i] for i in indices)


def get_nth_combination(
        iterable,
        *,
        items: int,
        index: int,
):
    """

    Credit to:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Examples:

    >>> wallet = [1] * 5 + [5] * 2 + [10] * 5 + [20] * 3
    >>> get_nth_combination(wallet, items=3, index=454)
    (20, 20, 20)
    >>> get_nth_combination(wallet, items=3, index=-1)
    (20, 20, 20)
    >>> get_nth_combination(wallet, items=3, index=455)
    Traceback (most recent call last):
     ...
    IndexError: Index 455 out of bounds
    >>> get_nth_combination(wallet, items=3, index=-454)
    (1, 1, 1)
    >>> get_nth_combination(wallet, items=len(wallet), index=0)
    (1, 1, 1, 1, 1, 5, 5, 10, 10, 10, 10, 10, 20, 20, 20)
    >>> get_nth_combination(wallet, items=len(wallet), index=1)
    Traceback (most recent call last):
     ...
    IndexError: Index 1 out of bounds

    """
    space = tuple(iterable)
    n = len(space)
    if items < 1:
        msg = f'Argument must be positive'
        raise ValueError(msg)
    if items > n:
        msg = f'Sample space has {n} items; Argument items cannot exceed that'
        raise ValueError(msg)
    c = 1
    k = min(items, n - items)
    for i in range(1, k + 1):
        c = c * (n - k + i) // i
    orig_index = index
    if index < 0:
        index += c
    if index < 0 or index >= c:
        msg = f'Index {orig_index} out of bounds'
        raise IndexError(msg)
    result = []
    while items:
        c, n, items = c * items // n, n - 1, items - 1
        while index >= c:
            index -= c
            c, n = c * (n - items) // n, n - 1
        result.append(space[-(n + 1)])
    return tuple(result)
