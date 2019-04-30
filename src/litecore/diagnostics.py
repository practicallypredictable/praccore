import functools
import logging
import time

from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

log = logging.getLogger(__name__)


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        wrapper.run_time = time.perf_counter() - start_time
        return value
    return wrapper


def counted(func: Callable) -> Any:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.times_called += 1
        return func(*args, **kwargs)
    wrapper.times_called = 0
    return wrapper


def should_log(level) -> bool:
    return __debug__ or level > logging.DEBUG


def _class_logger_name(class_obj) -> str:
    return f'{class_obj.__module__}.{class_obj.__qualname__}'


def class_logger(instance):
    return logging.getLogger(_class_logger_name(type(instance)))


def function_logger(func, *, name: Optional[str] = None):
    logger_name = name if name is not None else func.__module__
    return logging.getLogger(logger_name)


def _default_pre_message(func, *args, **kwargs) -> str:
    msg = (
        f'Calling {func.__module__}.{func.__qualname__} '
        f'with positional arguments: {args!r} '
        f'and keyword arguments: {kwargs!r}'
    )
    return msg


def _default_post_message(result) -> str:
    msg = (
        'Returned: {result!r}'
    )
    return msg


def logged(
        *,
        level: int = logging.DEBUG,
        name: Optional[str] = None,
        pre_message: Optional[Union[Callable, str]] = _default_pre_message,
        post_message: Optional[Union[Callable, str]] = _default_post_message,
) -> Callable:
    def decorator(func):
        if not should_log(level):
            return func

        logger = function_logger(func, name)

        if pre_message:
            if isinstance(pre_message, str):
                def _pre_msg(func4msg, *args4msg, **kwargs4msg):
                    return pre_message
            else:
                def _pre_msg(func4msg, *args4msg, **kwargs4msg):
                    return pre_message(func4msg, *args4msg, **kwargs4msg)

        if post_message:
            if isinstance(post_message, str):
                def _post_msg(result4msg):
                    return post_message
            else:
                def _post_msg(result4msg):
                    return post_message(result4msg)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if pre_message:
                logger.log(level, _pre_msg(func, *args, **kwargs))
            result = func(*args, **kwargs)
            if post_message:
                logger.log(level, _post_msg(func, result))
            return result
        return wrapper
    return decorator


logger = property(class_logger)
"""Property to support class-level logging.

Import this directly into class definitions that need class-level logging. This
is intended as an alternative to the simple mixin below for people who dislike
mixin classes.

Notice it must be imported directly into the class namespace.

The logger will have a name of the form '<class module>.<class qualname>'.

Examples:

>>> class LoggedExample:
...     from litecore.diagnostics import logger
...     def __init__(self, value):
...         self.logger.info('Setting value to %s', str(value))
...         self.value = value

"""


class LoggedMixin:
    """Mixin class to provide an easy-to-use class-level logger object.

    A class inheriting from this mixin will have a logger property that will
    have a name of the form '<class module>.<class qualname>'.

    """
    @property
    def logger(self):
        return class_logger(self)


def make_logged_collection_decorator(
        *,
        log_get: Optional[Callable] = None,
        log_set: Optional[Callable] = None,
        log_del: Optional[Callable] = None,
        default_level: int = logging.DEBUG,
        doc: Optional[str] = None,
):
    """Decorator factory to add logging to classes upon item access.

    This decorator factory works for either sequences or mappings. The
    keyword arguments log_get, log_set and log_del should be customized to
    work for the particular type of collection to be decorated, which
    will be implemented in the returned decorator.

    The keyword argument function signatures are:
        log_get(logger, level, instance, locator)
        log_set(logger, level, instance, locator, value)
        log_del(logger, level, instance, locator)

    For classes implementing a Sequence or MutableSequence interface,
    the locator will be an index or a slice. For classes implementing a
    Mapping or MutableMapping interface, the locator will be a key.

    A default level can be specified by keyword argument, in which case
    it will override the built-in default of logging.DEBUG in the returned
    decorator.

    If a docstring is supplied it will be applied to the decorator.
    Otherwise, the generic docstring below will be retained for the decorator.

    """
    def decorator(
            _cls=None,
            *,
            level: int = default_level,
    ):
        """Decorator to add logging to classes upon item access.

        Application of the decorator to a collection class will modify
        the class's __getitem__(), __setitem__() and __delitem__() methods
        (whichever exist) to log messages upon item access.

        The decorator may be applied without arguments (i.e., no parentheses),
        in which case the messages will be logged at DEBUG level. If the
        decorator is applied with parentheses, it takes a keyword argument
        level which defaults to DEBUG, but can be one of the other logging
        module levels such as INFO, WARNING, ERROR or CRITICAL.

        Note that this decorator will not modify the underlying class if the
        Python global __debug__ is False (i.e., Python is being run with the
        -O and -OO command-line flags), unless the logging level is higher
        than DEBUG.

        """
        def inner(cls):
            if not should_log(level):
                return cls

            logger = _class_logger_name(cls)

            if log_get is not None:
                cls_getitem = getattr(cls, '__getitem__', None)

                def __getitem__(self, locator):
                    log_get(logger, level, self, locator)
                    return cls_getitem(self, locator)

                if cls_getitem is not None:
                    cls.__getitem__ = __getitem__

            if log_set is not None:
                cls_setitem = getattr(cls, '__setitem__', None)

                def __setitem__(self, locator, value):
                    log_set(logger, level, self, locator, value)
                    return cls_setitem(self, locator, value)

                if cls_setitem is not None:
                    cls.__setitem__ = __setitem__

            if log_del is not None:
                cls_delitem = getattr(cls, '__delitem__', None)

                def __delitem__(self, locator):
                    log_del(logger, level, self, locator)
                    return cls_delitem(self, locator)

                if cls_delitem is not None:
                    cls.__delitem__ = __delitem__

            return cls

        if _cls is None:
            return inner
        else:
            return inner(_cls)

    if doc is not None:
        decorator.__doc__ = doc
    return decorator


def make_logged_mixin_factory(
        *,
        log_get: Optional[Callable] = None,
        log_set: Optional[Callable] = None,
        log_del: Optional[Callable] = None,
        default_level: int = logging.DEBUG,
):
    def factory(
        *,
        name: str,
        level: int = default_level,
        doc: Optional[str] = None,
    ):
        class _LoggedItemAccessMixin:
            """Mixin to add logging to classes upon item access.

            Classes which inherit from this mixin class will have overriden
            __getitem__(), __setitem__() and __delitem__() methods
            (whichever exist) to log messages upon item access.

            Logging may be surpressed if Python is running in optimized
            mode (e.g., with the -O or -OO command-line options), and if the
            mixin was created with the logging level set to anything greater
            than DEBUG. The logging level is set at the time of class creation
            by the factory function which created the class.

            The decision to log or not is determined at run-time. Furthermore,
            the mixin defines methods for all of __getitem__(), __setitem__()
            and __delitem__(), even if those methods don't exist in the
            other classes in the inheritance MRO. The mixin catches exceptions
            where the super() methods are called and do not exist.

            For these reason, use of this mixin class will be somewhat slower
            than using the related class decorator (see litecore.diagnostics).

            The class decorator can determine which methods are applicable at
            the time of class creation and make the necessary optimizations
            upfront once and for all.

            """
            __slots__ = ()

            if log_get is not None:
                def __getitem__(self, locator):
                    if should_log(level):
                        log_get(self.logger, level, self, locator)
                    return super().__getitem__(locator)

            if log_set is not None:
                def __setitem__(self, locator, value):
                    if should_log(level):
                        log_set(self.logger, level, self, locator, value)
                    super().__setitem__(locator, value)

            if log_del is not None:
                def __delitem__(self, locator, value):
                    if should_log(level):
                        log_del(self.logger, level, self, locator)
                    super().__delitem__(locator)

        _LoggedItemAccessMixin.__name__ = name
        if doc is not None:
            _LoggedItemAccessMixin.__doc__ = doc
        return _LoggedItemAccessMixin
    return factory


class LoggingContext:
    def __init__(
            self,
            logger: logging.Logger,
            *,
            level: Optional[int] = None,
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
        if self.handler is not None:
            self.logger.addHandler(self.handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.level is not None:
            self.logger.setLevel(self.save_level)
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            if self.close_handler:
                self.handler.close()
