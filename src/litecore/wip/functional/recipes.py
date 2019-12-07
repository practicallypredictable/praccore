import functools
import operator

from typing import (
    Any,
    Callable,
    Iterable,
)


def identity(value: Any) -> Any:
    """Returns its argument."""
    return value


def _constantly_return_value(value, *args, **kwargs):
    return value


def constantly_return(value: Any) -> Any:
    """Return a function which always returns the specified value.

    """
    f = functools.partial(_constantly_return_value, value)
    f.__doc__ = f'Always returns value {value}, irrespective of its arguments.'
    return f


class ArgsReversed:
    """Callable that reverses argument order of a two-argument callable.

    """

    def __init__(self, func):
        self.func = func

    def __call__(self, arg1, arg2):
        return self.func(arg2, arg1)

    def __repr__(self):
        return f'{type(self).__name__}(func={self.func!r})'


def reverse_args(func):
    return ArgsReversed(func)


class Composition:
    __slots__ = ('_first', '_rest')

    def __init__(self, funcs: Iterable[Callable]):
        funcs = tuple(reversed(funcs))
        self._first = funcs[0]
        self._rest = funcs[1:]

    def __call__(self, *args, **kwargs):
        value = self._first(*args, **kwargs)
        for func in self._rest:
            value = func(value)
        return value

    def __getstate__(self):
        return self._first, self._rest

    def __setstate__(self, state):
        self._first, self._rest = state

    @property
    def funcs(self):
        return tuple((self._first,) + self._rest)

    def __repr__(self) -> str:
        names = ' of '.join(func.__name__ for func in reversed(self.funcs))
        return f'<{type(self).__name__}: {names}'


def compose(*funcs):
    if not funcs:
        return identity
    elif len(funcs) == 1:
        return funcs[0]
    else:
        return Composition(funcs)


def complement(func: Callable[[Any], bool]) -> Callable[[Any], bool]:
    return compose(operator.not_, func)


def pipe(value: Any, *funcs):
    for func in funcs:
        value = func(value)
    return value


def side_effect(func: Callable, value: Any) -> Any:
    func(value)
    return value


def raises(func: Callable, exception: BaseException) -> bool:
    try:
        func()
        return False
    except exception:
        return True


class Juxtaposition:
    def __init__(self, funcs: Iterable[Callable]):
        self.funcs = tuple(funcs)

    def __call__(self, *args, **kwargs):
        return (f(*args, **kwargs) for f in self.funcs)

    def __repr__(self):
        return f'{type(self).__name__}(funcs={self.funcs})'


def juxtapose(*funcs):
    return Juxtaposition(funcs)
