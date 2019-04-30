import typing

import litecore.sentinel
from litecore import LitecoreError as _ErrorBase

NOT_SUPPLIED = litecore.sentinel.create(name='NOT_SUPPLIED')


class FailedMarker:
    def __init__(
            self,
            item: typing.Any,
            *,
            index: typing.Optional[int] = None,
    ) -> None:
        self.item = item
        self.index = index

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.item!r}, index={self.index!r})'

    def __eq__(self, other) -> bool:
        if type(self) is type(other):
            return self.item == other.item and self.index == other.index
        else:
            return False

    def __hash__(self) -> int:
        return hash(repr(self))


class ValidationError(_ErrorBase):
    """Base exception for validation errors."""

    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            value: typing.Any = NOT_SUPPLIED,
            from_exception: typing.Optional[Exception] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.value = value
        self.from_exception: Exception = from_exception


class InvalidValueError(ValidationError, ValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class InvalidKeyError(ValidationError, KeyError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            key: typing.Hashable,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.key: typing.Hashable = key


class SchemaError(ValidationError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            schema: typing.Any = NOT_SUPPLIED,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.schema = schema


class MultiValidationError(ValidationError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            top_level_errors: typing.Optional[typing.Collection] = None,
            underlying_errors: typing.Optional[typing.Collection] = None,
            results: typing.Any = NOT_SUPPLIED,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        if top_level_errors is None:
            top_level_errors = set()
        if underlying_errors is None:
            underlying_errors = set()
        self.top_level_errors: typing.Collection = top_level_errors
        self.underlying_errors: typing.Collection = underlying_errors
        self.results = results


class CoercionError(ValidationError, TypeError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            coerced: typing.Type,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.coerced: typing.Type = coerced


class InvalidConditionError(ValidationError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            expected: typing.Any,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.expected = expected


class InvalidTypeError(InvalidConditionError, TypeError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class StringDecodingError(InvalidValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            encoding: str,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.encoding: str = encoding


class ConstrainedValueError(InvalidValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            constraint: typing.Any,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
        self.constraint = constraint


class SpecifiedValueError(ConstrainedValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class RangeError(ConstrainedValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class LengthError(ConstrainedValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class SpecifiedPatternError(ConstrainedValueError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            *,
            pattern: str,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class ForbiddenKeyError(SchemaError, InvalidKeyError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)


class MissingKeyError(SchemaError, InvalidKeyError):
    def __init__(
            self,
            msg: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super().__init__(msg, **kwargs)
