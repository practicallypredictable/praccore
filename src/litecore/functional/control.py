import functools
import logging
import time

from typing import (
    Any,
    Callable,
    Optional,
)

log = logging.getLogger(__name__)


def synchronized(lock):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
            return wrapper
        return decorator


def sleeps(wait: float):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(wait)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def repeated(_func=None, *, times=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                value = func(*args, **kwargs)
            return value
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def hooked(
        func,
        *,
        before: Optional[Callable] = None,
        pre_modify: Optional[Callable] = None,
        after: Optional[Callable] = None,
        post_modify: Optional[Callable] = None,
) -> Any:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if before:
            before(func, *args, **kwargs)
        if pre_modify:
            value = func(pre_modify(*args, **kwargs))
        else:
            value = func(*args, **kwargs)
        if after:
            after(value, func, *args, **kwargs)
        if post_modify:
            return post_modify(value, func, *args, **kwargs)
        else:
            return value
    return wrapper
