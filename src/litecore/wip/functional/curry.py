

class curry:
    """

    >>> def mul(x: int, y: int): return x * y
    >>> mul = curry(mul)
    >>> mul.__name__
    'mul'
    >>> mul.__annotations__
    {'x': <class 'int'>, 'y': <class 'int'>}
    >>> double = mul(2)
    >>> double.args
    (2,)
    >>> double(10)
    20
    >>> curried_map = curry(map)
    >>> curried_map.__name__
    'map'
    >>> to_upper = curried_map(str.upper)
    >>> ''.join(to_upper('test'))
    'TEST'

    """

    def __init__(self, func, *args, **kwargs):
        if isinstance(func, functools.partial) or isinstance(func, curry):
            new_kwargs = {}
            if func.keywords:
                new_kwargs.update(func.keywords)
            new_kwargs.update(kwargs)
            kwargs = new_kwargs
            args = func.args + args
            func = func.func

        if kwargs:
            self._partial = functools.partial(func, *args, **kwargs)
        else:
            self._partial = functools.partial(func, *args)
        self.__doc__ = getattr(func, '__doc__', None)
        self.__name__ = getattr(func, '__name__', f'<{type(self).__name__}>')
        self.__module__ = getattr(func, '__module__', None)
        self.__qualname__ = getattr(func, '__qualname__', None)
        self.__annotations__ = getattr(func, '__annotations__', None)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return type(self)(self, instance)

    @property
    def func(self):
        return self._partial.func

    @property
    def args(self):
        return self._partial.args

    @property
    def keywords(self):
        return self._partial.keywords

    def __repr__(self):
        return f'<{type(self).__name__} of {self.func}>'

    def __eq__(self, other):
        return (
            isinstance(other, curry)
            and self.func == other.func  # noqa: W503
            and self.args == other.args  # noqa: W503
            and self.keywords == other.keywords  # noqa: W503
        )

    def __hash__(self):
        frozen_kwargs = frozenset(
            self.keywords.items() if self.keywords else None
        )
        return hash((self.func, self.args, frozen_kwargs))

    def bind(self, *args, **kwargs):
        return type(self)(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        try:
            return self._partial(*args, **kwargs)
        except TypeError:
            return self.bind(*args, **kwargs)
