import collections

from typing import (
    Callable,
)


class classproperty:
    def __init__(self, func: Callable):
        self._func = func

    def __get__(self, instance, cls):
        return self._func(cls)


def subclasses(cls):
    try:
        queue = collections.deque(cls.__subclasses__())
    except (AttributeError, TypeError) as err:
        msg = f'expected type object, got {cls!r}'
        raise TypeError(msg) from err
    seen = set()
    classes = []
    while queue:
        cls = queue.popleft()
        if cls in seen:
            continue
        seen.add(cls)
        classes.append(cls)
        queue.extend(cls.__subclasses__())
    return classes
