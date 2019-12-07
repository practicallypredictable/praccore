from typing import (
    Any,
    Tuple,
)

import litecore.validation.base as base
import litecore.validation.exceptions as exc

DEFAULT_TRUE_STRINGS = ('true', 't', 'yes', 'y', 'on', '1', 'enable')
DEFAULT_FALSE_STRINGS = ('false', 'f', 'no', 'n', 'off', '0', 'null', 'disable')


class Boolean(base.Simple):
    """Validates boolean values and common string synonyms.

    Examples:

    >>> v = Boolean(coerce=True)
    >>> v(False)
    False
    >>> v('Y')
    True
    >>> v('0')
    False
    >>> v('On')
    True
    >>> v(None)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value None incompatible with <class 'bool'> ...
    >>> Boolean(nullable=True)(None)

    """
    __slots__ = base.get_slots(base.Simple) + (
        'true_strings',
        'false_strings',
    )
    default_coerce_type = bool

    def __init__(
            self,
            *,
            true_strings: Tuple[str] = DEFAULT_TRUE_STRINGS,
            false_strings: Tuple[str] = DEFAULT_FALSE_STRINGS,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.true_strings = set(s.casefold() for s in true_strings)
        self.false_strings = set(s.casefold() for s in false_strings)

    def _validate(self, value: Any) -> None:
        if not isinstance(value, bool):
            raise exc.ValidationTypeError(value, self, bool)
        return super()._validate(value)

    def _coerce_value(self, value: Any) -> bool:
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            if value.casefold() in self.true_strings:
                return True
            elif value.casefold() in self.false_strings:
                return False
        raise exc.ValidationTypeError(value, self, self.coerce_type)
