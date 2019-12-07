import abc
import re

from typing import (
    Any,
    Optional,
    Union,
)

import litecore.validation.base as base
import litecore.validation.length as length
import litecore.validation.specified as specified
import litecore.validation.exceptions as exc


class RegEx(base.Validator):
    __slots__ = base.get_slots(base.Validator) + (
        'pattern',
        'flags',
        '_compiled',
    )

    def __init__(
        self,
        *,
        pattern: Optional[Union[str, bytes, re.Pattern]] = None,
        flags: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.pattern = pattern
        self.flags = flags
        if isinstance(pattern, re.Pattern):
            self._compiled = pattern
        else:
            self._compiled = re.compile(pattern, flags)

    def _validate(self, value: Any) -> Any:
        if not re.match(self._compiled, value):
            raise exc.PatternError(value, self)
        return super()._validate(value)


@base.abstractslots(('regex',))
class HasRegEx(base.Validator):
    __slots__ = ()

    def __init__(
        self,
        *,
        regex: Optional[RegEx] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.regex = regex

    @abc.abstractmethod
    def _validate(self, value: Any) -> Any:
        if self.regex is not None:
            value = self.regex(value)
        return super()._validate(value)


class String(HasRegEx, length.HasLength, specified.SimpleChoices):
    """

    Examples:

    """
    __slots__ = ('encoding',) + base.combine_slots(
        HasRegEx,
        length.HasLength,
        specified.SimpleChoices,
    )
    default_coerce_type = str

    def __init__(
            self,
            *,
            encoding: Optional[str] = 'utf-8',
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.encoding = encoding

    def _validate(self, value: Any) -> Any:
        if isinstance(value, bytes) and self.encoding is not None:
            try:
                value = value.decode(self.encoding)
            except UnicodeDecodeError as err:
                args = (value, self, str, err)
                raise exc.ValidationTypeError(*args) from err
        return super()._validate(value)
