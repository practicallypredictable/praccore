import itertools

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
)


def force_reverse(iterable: Iterable[Any]) -> Iterator[Any]:
    try:
        return reversed(iterable)
    except TypeError:
        return reversed(list(iterable))


def iter_with(context_manager: Iterable[Any]) -> Iterator:
    """Wrap an iterable context manager so it closes when consumed.

    Allows a context manager which is also iterable to be used lazily or
    asynchronously. Whatever resources are used by the context manager will
    be released automatically when the iterator is consumed.

    Arguments:
        context_manager: context manager which is also an iterable

    Yields:
        each item of the iterable

    """
    with context_manager as iterable:
        for item in iterable:
            yield item


def tabulate(expr: Callable[[int], Any], *, start: int = 0) -> Iterator:
    """Return an infinite iterator of terms based upon an expression.

    Based upon the expressions, which takes one integer argument, reqturn
    a mathematical or other sequence counting up from the given start point.

    Arguments:
        expression: callable taking one integer argument, returning each term
            of the sequence

    Keyword Arguments:
        start: integral start point of the sequence (optional; default is 0)

    Returns:
        infinite iterator of sequence terms starting at the start index.

    Examples:

    >>> from litecore.irecipes.common import take
    >>> list(take(5, tabulate(lambda n: n ** 2)))
    [0, 1, 4, 9, 16]
    >>> word = 'supercalifragilistic'
    >>> list(take(5, tabulate(lambda n: word[:n], start=1)))
    ['s', 'su', 'sup', 'supe', 'super']

    """
    return map(expr, itertools.count(start=start))


def iterate(func: Callable[[Any], Any], *, start: Any) -> Iterator:
    """Yield the endlessly-iterated values of a function.

    Starting with a start value, feed the output value of the function as the
    input value for the next iteration of the function.

    The function should not modify the value of its argument.

    In mathematical notation, if the start value is x and the function is f(x),
    the generator yields:
        x, f(x), f(f(x)), f(f(f(x))), ...

    Arguments:
        func: callable taking a value and returning a value

    Keyword Arguments:
        start: the starting value for the iteration

    Yields:
        iterated function values starting with the start value

    Examples:

    >>> from litecore.irecipes.common import take
    >>> logistic_map = iterate(lambda x: 3.8 * x * (1-x), start=0.4)
    >>> [round(x, 2) for x in take(5, logistic_map)]
    [0.4, 0.91, 0.3, 0.81, 0.6]
    >>> dumb_count = iterate(lambda n: n+1, start=0)
    >>> import itertools
    >>> take(5, dumb_count) == take(5, itertools.count())
    True
    >>> palindrome = 'race car'
    >>> take(4, iterate(lambda s: s[::-1], start=palindrome))
    ['race car', 'rac ecar', 'race car', 'rac ecar']

    """
    x = start
    while True:
        yield x
        x = func(x)


def iter_except(
        func: Callable,
        until_raises: BaseException,
        *,
        first: Optional[Callable[[], Any]] = None,
) -> Iterator:
    """Call a function repeatedly until a specified exception is raised.

    This is the same as the function from the standard library itertools
    recipes. See some additional useful examples at:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    Converts a call-until-exception interface to an iterator interface.

    Arguments:
        func: zero-argument callable
        until_raises: the exception to be detected to break the infinite loop

    Keyword Arguments:
        first: zero-argument callable to call before beginning the iteration
            (optional; default is None)

    Yields:
        result of calling the first() function (if applicable), then the result
        of repeated calls to func()

    Examples:

    >>> s = set('abracadabra')
    >>> sorted(item for item in iter_except(s.pop, KeyError))
    ['a', 'b', 'c', 'd', 'r']
    >>> s
    set()

    """
    try:
        if first is not None:
            yield first()
        while True:
            yield func()
    except until_raises:
        pass


def repeatfunc(
        func: Callable,
        *args,
        times: Optional[int] = None,
) -> Iterator:
    """

    >>> import random
    >>> random.seed(1)
    >>> list(repeatfunc(random.randint, 0, 1000, times=5))
    [137, 582, 867, 821, 782]
    >>> [round(r, 3) for r in repeatfunc(random.random, times=3)]
    [0.063, 0.118, 0.761]

    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    return itertools.starmap(func, itertools.repeat(args, times))
