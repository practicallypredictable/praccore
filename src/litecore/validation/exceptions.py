from litecore import LitecoreError as _LCError


class ValidationError(_LCError):
    """Base exception type for validation errors."""


class SimpleTypeError(ValidationError, TypeError):
    """Encountered a value with an incorrect simple type."""

    def __init__(
            self,
            value,
            target_type,
            from_err=None,
            msg=None,
    ):
        self.value = value
        self.target_type = target_type
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, target_type)
        super().__init__(msg)

    def default_message(self, value, target_type):
        return f'value {value!r} incompatible with {target_type!r}'

    def __reduce__(self):
        args = (
            self.value,
            self.target_type,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class ValidationValueError(ValidationError, ValueError):
    """Encountered an invalid value."""

    def __init__(
            self,
            value,
            validator,
            from_err=None,
            msg=None,
    ):
        self.value = value
        self.validator = validator
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, validator)
        super().__init__(msg)

    def default_message(self, value, validator):
        return f'value {value!r} rejected by validator {validator!r}'

    def __reduce__(self):
        args = (
            self.value,
            self.validator,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class ValidationTypeError(ValidationError, TypeError):
    """Encountered a value of an invalid type."""

    def __init__(
            self,
            value,
            validator,
            target_type=None,
            from_err=None,
            msg=None,
    ):
        self.value = value
        self.validator = validator
        self.target_type = target_type
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, validator, target_type)
        super().__init__(msg)

    def default_message(self, value, validator, target_type):
        if target_type is not None:
            return (
                f'value {value!r} incompatible with {target_type!r} '
                f'for validator {validator!r}'
            )
        else:
            return (
                f'value {value!r} type {type(value)} '
                f'rejected by validator {validator!r}'
            )

    def __reduce__(self):
        args = (
            self.value,
            self.validator,
            self.target_type,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class MultiStepValidationError(ValidationError):
    """Encountered at least one error in a multi-step validation."""

    def __init__(
            self,
            value,
            validator,
            details,
            msg=None,
    ):
        self.value = value
        self.validator = validator
        self.details = details
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, validator, details)
        super().__init__(msg)

    def default_message(self, value, validator, details):
        return (
            f'value {value!r} rejected by validator {validator!r}; '
            f'details: {details!r}'
        )

    def __reduce__(self):
        args = (
            self.value,
            self.validator,
            self.details,
            self._msg,
        )
        return (type(self), args)


class ContainerTypeError(ValidationTypeError):
    """Expected a valid container and received something else."""


class ContainerItemError(ValidationError):
    pass


class NonUniqueContainerItemError(ContainerItemError, ValueError):
    """Encountered an unexpected non-unique container item."""

    def __init__(
            self,
            value,
            path,
            msg=None,
    ):
        self.value = value
        self.path = path
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, path)
        super().__init__(msg)

    def default_message(self, value, validator, path):
        return f'value {value!r} (container path {path!r}) is a duplicate'

    def __reduce__(self):
        args = (
            self.value,
            self.path,
            self._msg,
        )
        return (type(self), args)


class ContainerItemValueError(ContainerItemError, ValueError):
    """Encountered an invalid container item."""

    def __init__(
            self,
            value,
            path,
            from_err,
            msg=None,
    ):
        assert from_err is not None
        self.value = value
        self.path = path
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, path, from_err)
        super().__init__(msg)

    def default_message(self, value, path, from_err):
        return (
            f'value {value!r} (container path {path!r}) '
            f'rejected with error {from_err!r}'
        )

    def __reduce__(self):
        args = (
            self.value,
            self.validator,
            self.path,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class ContainerItemTypeError(ContainerItemError, TypeError):
    """Encountered a container item with an invalid type."""

    def __init__(
            self,
            value,
            path,
            target_type,
            from_err,
            msg=None,
    ):
        assert from_err is not None
        self.value = value
        self.path = path
        self.target_type = target_type
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, path, target_type, from_err)
        super().__init__(msg)

    def default_message(self, value, path, target_type, from_err):
        if target_type is not None:
            return (
                f'value {value!r} (container path {path!r}) '
                f'incompatible with {target_type!r} '
                f', rejected with error {from_err!r}'
            )
        else:
            return (
                f'value {value!r} (container path {path!r}) '
                f'type rejected with error {from_err!r}'
            )

    def __reduce__(self):
        args = (
            self.value,
            self.path,
            self.target_type,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class ContainerItemKeyError(ContainerItemError, KeyError):
    """Encountered a mapping container item with an invalid key."""

    def __init__(
            self,
            value,
            key,
            from_err,
            msg=None,
    ):
        assert from_err is not None
        self.value = value
        self.key = key
        self.from_err = from_err
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, key, from_err)
        super().__init__(msg)

    def default_message(self, value, key, from_err):
        return (
            f'value {value!r} (container key {key!r}) '
            f'with error {from_err!r}'
        )

    def __reduce__(self):
        args = (
            self.value,
            self.key,
            self.from_err,
            self._msg,
        )
        return (type(self), args)


class ContainerValidationError(ValidationError):
    """Encountered at least one error in validating container items."""

    def __init__(
            self,
            value,
            validator,
            errors,
            msg=None,
    ):
        self.value = value
        self.validator = validator
        self.errors = errors
        self._msg = msg
        if msg is None:
            msg = self.default_message(value, validator, errors)
        super().__init__(msg)

    def default_message(self, value, validator, errors):
        return (
            f'value {value!r} rejected by validator {validator!r} '
            f'with {len(errors)} error(s): {errors!r}'
        )

    def __reduce__(self):
        args = (
            self.value,
            self.validator,
            self.errors,
            self._msg,
        )
        return (type(self), args)


class CoercionError(ValidationTypeError):
    """Encountered error attempting to coerce a value to another type."""


class ParseError(ValidationValueError):
    """Encountered error attempting to parse a value."""


class ValidationHookError(ValidationValueError):
    """Encountered error during user-provided validation hook."""


class SpecifiedValueError(ValidationValueError):
    """Encountered a value unequal to one or more specified values."""


class ConstantError(SpecifiedValueError):
    """Encountered a value unequal to a required constant."""

    def default_message(self, value, validator):
        return f'value must equal {validator.value!r}; got {value!r}'


class ChoiceError(SpecifiedValueError):
    """Encountered a value unequal to one or more specified values."""

    def default_message(self, value, validator):
        return (
            f'invalid value {value!r}; '
            f'must be in {sorted(validator.values)}'
        )


class EnumeratedChoiceError(SpecifiedValueError):
    """Encountered a value unequal to any of the valid enumerated values."""

    def default_message(self, value, validator):
        return (
            f'invalid value {value!r}; '
            f'must be in {list(validator.values)}'
        )


class ExcludedValueError(SpecifiedValueError):
    """Encountered a value equal to one or more excluded values."""


class ExcludedChoiceError(ExcludedValueError):
    """Encountered a value equal to one of several excluded values."""

    def default_message(self, value, validator):
        return (
            f'invalid value {value!r}; '
            f'must not be in {sorted(validator.values)}'
        )


class ExcludedEnumeratedChoiceError(ExcludedValueError):
    """Encountered a value equal to one of several excluded enumerated values."""

    def default_message(self, value, validator):
        return (
            f'invalid value {value!r}; '
            f'must not be in {list(validator.values)}'
        )


class BoundError(ValidationValueError):
    """Encountered a value that violates a bound."""


class LowerBoundError(BoundError):
    """Encountered a value that violates a lower bound."""

    def default_message(self, value, validator):
        symbol = '>=' if validator.lower_inclusive else '>'
        return f'value {value!r} not {symbol} lower bound {validator.lower!r}'


class UpperBoundError(BoundError):
    """Encountered a value that violates an upper bound."""

    def default_message(self, value, validator):
        symbol = '<=' if validator.upper_inclusive else '<'
        return f'value {value!r} not {symbol} upper bound {validator.upper!r}'


class LengthError(ValidationValueError):
    """Encountered a value that violates a length bound."""

    def default_message(self, value, validator):
        return f'value {value!r} has invalid length {len(value)}'


class MinLengthError(LengthError):
    """Encountered a value that is too short."""

    def default_message(self, value, validator):
        return (
            f'value {value!r} has length {len(value)} '
            f'< bound {validator.at_least!r}'
        )


class MaxLengthError(LengthError):
    """Encountered a value that is too long."""

    def default_message(self, value, validator):
        return (
            f'value {value!r} has length {len(value)} '
            f'> bound {validator.at_most!r}'
        )


class PatternError(ValidationValueError):
    """Encountered a value that does not match a regex pattern."""

    def default_message(self, value, validator):
        return f'value {value!r} does not match patter {validator.regex!r}'


class TimeZoneError(ValidationValueError):
    """Encountered inconsistent timezone information."""


class NaNError(ValidationValueError):
    """Encountered a non-a-number in an invalid circumstance."""
