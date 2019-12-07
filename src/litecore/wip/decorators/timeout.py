import functools
import multiprocessing
import signal
import time

from typing import (
    Callable,
    Optional,
)


class TimeoutError(RuntimeError):
    """Function run time exceeded timeout threshold."""


def timeout_signal(
        seconds: int,
        *,
        message: Optional[str] = None,
) -> Callable:
    if message is None:
        message = f'function timed out after {seconds} seconds'

    def decorator(func):
        if not seconds:
            return func

        def _timeout_handler(signum, frame):
            raise TimeoutError(message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            prior = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, prior)
            return result
        return wrapper
    return decorator


def _try_func(queue, func, *args, **kwargs):
    try:
        # if function call successful, put tuple (True, <result>)
        queue.put((True, func(*args, **kwargs)))
    except Exception as err:
        # if exception, put tuple (False, <exception instance>)
        queue.put((False, err))


class _TimeoutHandler:
    def __init__(
            self,
            func: Callable,
            *,
            timeout: int,
            message: str,
            sleep: float,
    ):
        self.func = func
        self.timeout = timeout
        self.message = message
        self.sleep = sleep

    def __repr__(self):
        return (
            f'<{type(self).__name__}('
            f'timeout={self.timeout}'
            f'message={self.message}'
            f', sleep={self.sleep}'
            f')>'
        )

    def __call__(self, *args, **kwargs):
        self.queue = multiprocessing.Queue(1)
        args = (self.queue, self.func) + args
        self.process = multiprocessing.Process(
            target=_try_func,
            args=args,
            kwargs=kwargs,
        )
        self.process.daemon = True
        limit_time = time.time() + self.timeout
        self.process.start()
        while self.queue.empty():
            if time.time() > limit_time:
                self._terminate_and_raise()
            time.sleep(self.sleep)
        worked, result = self.queue.get()
        if worked:
            return result
        else:
            raise result

    def _terminate_and_raise(self):
        if self.process.is_alive():
            self.process.terminate()
        raise TimeoutError(self.message)


def timeout_process(
        seconds: int,
        *,
        message: Optional[str] = None,
        sleep: float = 0.01,
) -> Callable:
    if message is None:
        message = f'function timed out after {seconds} seconds'

    def decorator(func):
        if not seconds:
            return func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = _TimeoutHandler(
                func, timeout=seconds, message=message, sleep=sleep)
            return handler(*args, **kwargs)
        return wrapper
    return decorator
