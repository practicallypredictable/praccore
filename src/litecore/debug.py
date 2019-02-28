import functools
import logging

from typing import (
    Any,
    Callable,
    Optional,
)

log = logging.getLogger(__name__)


class LoggingContext:
    def __init__(
            self,
            logger: logging.Logger,
            *,
            level: Optional[Any] = None,
            handler: logging.Handler = None,
            close_handler: bool = True,
    ) -> None:
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close_handler = close_handler

    def __enter__(self):
        if self.level is not None:
            self.save_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.level is not None:
            self.logger.setLevel(self.save_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close_handler:
            self.handler.close()


def shadow(func: Callable, *, output: Callable = print):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        msg = f'{func.__qualname__}(args={args!r}, kwargs={kwargs!r})'
        output(msg)
        result = func(*args, **kwargs)
        msg = f'  -> {result!r}'
        output(msg)
        return result
    return wrapper
