"""Functions specialized for numerical computations on iterables.

"""
import collections
import itertools
import numbers
import operator

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
)

import litecore.irecipes.common as _common

from litecore.sentinels import NO_VALUE as _NO_VALUE


def inner_product(
    left: Iterable[numbers.Number],
    right: Iterable[numbers.Number],
    *,
    op: Callable[[Any, Any], Any] = operator.mul,
    reduction: Callable[[Iterable[Any]], Any] = sum,
) -> numbers.Number:
    """Return generalized inner product between two iterables.

    Applies an aggregation (default is sum) over a binary operation
    (default is multiplication) applied to the zipped items of two
    iterables. For iterables of numbers, this is the usual vector
    dot product.

    The two iterables must be the same (finite) length.

    Arguments:
        left: first iterable
        right: second iterable

    Keyword Arguments:
        op: two-argument callable returning a value
            (default is multiplication operator)
        reduction: callable accepting an iterable which returns a single
            value (default is built-in sum function)

    Returns:
        numeric result of the computation

    Examples:

    >>> inner_product(range(1, 5), range(1, 5)) == 1 + 4 + 9 + 16
    True
    >>> c1 = [complex(1, -1), complex(3, 5)]
    >>> c2 = [complex(2, 2), complex(-3, 1)]
    >>> c3 = ()
    >>> inner_product(c1, c2)
    (-10-12j)
    >>> inner_product(c1, c3)
    Traceback (most recent call last):
     ...
    ValueError: vectors of incompatible lengths
    >>> cost = [3, 2, 7, 5]
    >>> incremental = [8, 7, 1, 4]
    >>> inner_product(cost, incremental, op=operator.add, reduction=min)
    8

    """
    items = itertools.zip_longest(left, right, fillvalue=_NO_VALUE)
    try:
        return reduction(op(x, y) for x, y in items)
    except TypeError:
        msg = f'vectors of incompatible lengths'
        raise ValueError(msg) from None


def difference(iterable: Iterable[numbers.Number]) -> Iterator[numbers.Number]:
    """Take first differences of items of an iterable.

    Assumes the subtraction operator makes sense for each item of the
    iterable.

    Arguments:
        iterable: object the items of which are to be differenced

    Returns:
        iterator of the first differences

    Examples:

    >>> list(difference(range(10)))
    [1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> list(difference([x * x for x in range(10)]))
    [1, 3, 5, 7, 9, 11, 13, 15, 17]
    >>> list(difference(difference([x * x for x in range(10)])))
    [2, 2, 2, 2, 2, 2, 2, 2]

    """
    return (x2 - x1 for x1, x2 in _common.pairwise(iterable))


def proportional_change(
        iterable: Iterable[numbers.Number],
        *,
        zero_divide_value: Optional[Any] = _NO_VALUE,
) -> Iterator[Any]:
    """Return proportional changes of the items of an iterable.

    Assumes the subtraction and division operators makes sense for each
    item of the iterable. A ZeroDivisionError will be raised if any of
    the items of the original iterable are zero.

    To get percent changes, just multiply the items from this function
    by 100.

    To get log changes, take the desired logarithm.

    Arguments:
        iterable: object the items of which are to be differenced

    Returns:
        iterator of the proportional changes

    Examples:

    >>> [round(p, 3) for p in proportional_change(range(1, 10))]
    [1.0, 0.5, 0.333, 0.25, 0.2, 0.167, 0.143, 0.125]
    >>> [round(p, 3) for p in proportional_change(range(0, 10))]
    Traceback (most recent call last):
     ...
    ZeroDivisionError: division by zero
    >>> [round(p, 3) for p in proportional_change(
    ...     range(0, 10), zero_divide_value=float('NaN'))
    ... ]
    [nan, 1.0, 0.5, 0.333, 0.25, 0.2, 0.167, 0.143, 0.125]

    """
    for x1, x2 in _common.pairwise(iterable):
        try:
            yield (x2 - x1) / x1
        except ZeroDivisionError:
            if zero_divide_value is not _NO_VALUE:
                yield zero_divide_value
            else:
                raise


def round_items(
        iterable: Iterable[numbers.Number],
        digits: Optional[int] = None,
        *,
        skipvalue: Optional[Any] = None,
) -> Iterator[numbers.Number]:
    """Return iterator of items with built-in round() applied.

    The optional keyword argument skipvalue can be used to skip over
    certain values (e.g., None, the default). Items not skipped
    will be rounded per the built-in round() function using the digits
    argument.

    Arguments:
        iterable: object with items to be rounded
        digits: number of digits for rounding (optional; default is
            None); see the built-in round() function for more details

    Keyword Arguments:
        skipvalue: specifies item values to pass through without
            rounding (optional; default is None)

    Returns:
        iterator of rounded (or skipped) items of the iterable

    Examples:

    >>> data = [1, 1.1, 1.23, 1.456, 1.7890, 2.98500, 2.98501]
    >>> list(round_items(data, 2))
    [1, 1.1, 1.23, 1.46, 1.79, 2.98, 2.99]

    """
    return (
        round(item, digits)
        if item is not skipvalue else skipvalue
        for item in iterable
    )


def simple_ma(
    window_size: int,
    iterable: Iterable[numbers.Number],
    *,
    prepend: Optional[Any] = _NO_VALUE,
) -> Iterator[numbers.Number]:
    """Return iterator of simple moving average values.

    Given an iterable of (assumed numeric) items, compute the simple
    moving average (SMA) of the items based upon a window of specified
    width.

    The SMA value is the simple (equal-weighted) average of the previous
    items of the iterable, taken over a window of the specified size.

    For example, for items of the iterable x0, x1, x2, x3, ... and a
    window of size 3, the SMA(3) (ignoring any prepended markers) is:

        sma0 = (x0+x1+x2)/3, sma1 = (x1+x2+x3)/3, sma2 = (x2+x3+x4)/3, ...

    If the passed iterable has fewer items than the SMA window size,
    an empty iterator will be returned.

    The prepend keyword argument specifies whether to include a filler
    marker (e.g., None or float('NaN')) for the initial items of the
    SMA (i.e., before enough items have been seen to compute the first
    SMA item). This assumes that there are enough items to yield at least
    one real SMA item.

    Arguments:
        window_size: positive integral window size
        iterable: object with numeric items

    Keyword Arguments:
        prepend: filler marker (optional; default is to have no
            filler and effectively lag the SMA returned values)

    Returns:
        iterator of the SMA values, prepended (if applicable) with the
        specified filler marker

    Examples:

    >>> prices = [100, 103, 106, 106, 109, 100, 103]
    >>> list(round_items(simple_ma(3, prices)))
    [103, 105, 107, 105, 104]
    >>> sma = list(round_items(simple_ma(3, prices, prepend=None)))
    >>> sma
    [None, None, 103, 105, 107, 105, 104]
    >>> round(sum(prices[:3]) / 3) == sma[2]
    True
    >>> round(sum(prices[1:4]) / 3) == sma[3]
    True
    >>> list(simple_ma(3, [], prepend=None))
    []
    >>> list(simple_ma(3, [1], prepend=None))
    []
    >>> list(simple_ma(3, [1, 2], prepend=None))
    []
    >>> list(round_items(simple_ma(3, [1, 2, 3], prepend=None)))
    [None, None, 2]

    """
    iterator = iter(iterable)
    current_items = collections.deque(itertools.islice(iterator, window_size - 1))
    next_value, iterator = _common.peek(iterator, default=_NO_VALUE)
    if next_value is _NO_VALUE:
        # we don't have enough items to even yield one real SMA item
        return iter(())
    if prepend is not _NO_VALUE:
        for _ in range(window_size - 1):
            yield prepend
    pop_old = current_items.popleft
    push = current_items.append
    current_items.appendleft(0)
    current_sum = sum(current_items)
    for new_item in iterator:
        push(new_item)
        current_sum += new_item - pop_old()
        yield current_sum / window_size


def exponential_ma(
    iterable: Iterable[numbers.Number],
    *,
    factor: numbers.Real,
    start: Any = _NO_VALUE,
) -> Iterator[numbers.Number]:
    """Return iterator of exponential moving average values.

    Given an iterable of (assumed numeric) items, compute the exponential
    moving average (EMA) of the items based upon a specified scaling
    factor which captures how quickly prior information decays.

    For example, for items of the iterable x0, x1, x2, x3, ... and a
    factor of 0.8, the EMA (assuming the default start value) is:

        ema0 = x0, ema1 = (0.8*x1 + 0.2*ema0), ema2 = (0.8*x2 + 0.2*ema1), ...

    Note therie is no prepend functionality. The EMA is always aligned
    with the original series.

    Arguments:
        items: positive integral window size
        iterable: object with numeric items

    Keyword Arguments:
        factor: scaling factor (strictly between 0 and 1)
        start: initialization value of the EMA (optional; default is
            to use the first value of the original iterable as the start
            value)

    Yields:
        each EMA value

    Raises:
        ValueError: if factor is not strictly between 0 and 1

    Examples:

    >>> prices = [100, 103, 106, 106, 109, 100, 103]
    >>> ema = list(round_items(exponential_ma(prices, factor=0.5), 4))
    >>> ema
    [100, 101.5, 103.75, 104.875, 106.9375, 103.4688, 103.2344]
    >>> list(exponential_ma([], factor=0.8))
    []
    >>> list(exponential_ma([1], factor=0.8))
    [1]
    >>> list(exponential_ma([1, 2], factor=0.8))
    [1, 1.8]

    """
    if not 0 < factor < 1:
        msg = f'factor must be strictly between 0 and 1'
        raise ValueError(msg)
    factor_complement = 1.0 - factor
    iterator = iter(iterable)
    first = next(iterator, _NO_VALUE)
    if first is _NO_VALUE:
        return iter(())
    ema = start if start is not _NO_VALUE else first
    yield ema
    for item in iterator:
        ema = factor * item + factor_complement * ema
        yield ema
