import abc
import copy
import logging
import re
import typing

import litecore.validate.exceptions as exc

log = logging.getLogger(__name__)
_validator_type_registry = {}


class Validator(abc.ABC):
    preempt_validation = False

    def __init__(
            self,
            *,
            post_validation_hook: typing.Optional[typing.Callable] = None,
    ) -> None:
        self._params = ('post_validation_hook',)
        self.post_validation_hook = post_validation_hook

    def register_params(self, params: typing.Iterable[str]) -> None:
        if __debug__:
            if any(param in self._params for param in params):
                msg = (
                    f'Attempt to register new params {params} '
                    f'clashes with existing params {self._params}'
                )
                raise ValueError(msg)
        self._params = self._params + params

    def validate(self, value: typing.Any) -> typing.Any:
        if type(self).preempt_validation and self.preemptive_validation(value):
            return value
        value = self.detailed_validation(value)
        if self.post_validation_hook is not None:
            value = self.post_validation_hook(value)
        return value

    __call__ = validate

    def preemptive_validation(self, value: typing.Any) -> bool:
        return False

    @abc.abstractmethod
    def detailed_validation(self, value: typing.Any) -> typing.Any:
        raise NotImplementedError()

    @property
    def params(self) -> typing.Iterator[typing.Tuple[str, typing.Any]]:
        for param in self._params:
            value = getattr(self, param)
            if value:
                yield param, value

    def __repr__(self) -> str:
        params = ', '.join(f'{param}={value}' for param, value in self.params)
        return f'{type(self).__name__}({params})'

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return tuple(self.params) == tuple(other.params)

    # TODO: pickling, serialization
    # https://bitbucket.org/cottonwood-tech/validx/src/9289d87a5b31c29de279370b8486aaae9f4be0aa/validx/py/abstract.py?at=default&fileviewer=file-view-default


class Anything(Validator):
    preempt_validation = True

    def preemptive_validation(self, value: typing.Any) -> bool:
        return True

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        return value


class Constant(Validator):
    preempt_validation = True

    def __init__(self, *, value: typing.Any, **kwargs) -> None:
        super().__init__(**kwargs)
        self.register_params(('value',))
        self.value = value

    def preemptive_validation(self, value: typing.Any) -> bool:
        if value != self.value:
            msg = f'value must equal constant {self.value!r}'
            raise exc.SpecifiedValueError(
                msg,
                expected=self.value,
                actual=value,
            )
        return True

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        return value


class Range(Validator):
    def __init__(
        self,
        *,
        min_value: typing.Optional[int] = None,
        max_value: typing.Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if __debug__:
            if min_value is not None:
                min_value = int(min_value)
                if min_value < 0:
                    msg = f'min argument must be positive'
                    raise ValueError(msg)
            if max_value is not None:
                max_value = int(max_value)
                if max_value < 0:
                    msg = f'max argument must be positive'
                    raise ValueError(msg)
                elif min_value is not None and max_value < min_value:
                    msg = f'max argument cannot be less than min argument'
                    raise ValueError(msg)
        self.register_params(('min_value', 'max_value'))
        self.min_value = min_value
        self.max_value = max_value

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        if self.min_value is not None and value < self.min_value:
            raise exc.RangeError(constraint=self, value=value)
        if self.max_value is not None and value > self.max_value:
            raise exc.RangeError(constraint=self, value=value)
        return value


class OneOf(Validator):
    def __init__(
        self,
        values: typing.Iterable[typing.Any],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        values = set(values)
        if __debug__:
            if len(values) < 1:
                msg = f'must provide at least one value'
                raise ValueError(msg)
        self.register_params(('values',))
        self.values: set = set(values)

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        if self.values and value not in self.values:
            raise exc.SpecifiedValueError(
                constraint=self,
                value=value,
            )
        return value


class Length(Validator):
    def __init__(
        self,
        *,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('min_length', 'min_length'))
        self.min_value = min_length
        self.max_value = min_length
        self._range = Range(min_value=min_length, max_value=max_length)

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        try:
            length = len(value)
        except TypeError as err:
            msg = 'Attempt to validate value {value!r} with no length'
            raise exc.ValidationError(msg) from err
        try:
            return self._range(length)
        except exc.RangeError:
            raise exc.LengthError(constraint=self, value=value)
        return value


class Pattern(Validator):
    def __init__(
        self,
        *,
        regex: typing.Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('regex',))
        self.regex = regex
        if regex is not None:
            self._compiled = re.compile(regex)

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        if self.regex is not None and not re.match(self._compiled, value):
            raise exc.SpecifiedPatternError(pattern=self.regex, value=value)
        return value


class Nullable(Validator):
    preempt_validation = True

    def __init__(
            self,
            *,
            nullable: bool = False,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('nullable',))
        self.nullable = nullable

    def preemptive_validation(self, value: typing.Any) -> bool:
        if value is None:
            if not self.nullable:
                msg = f'value cannot be None'
                raise exc.InvalidValueError(msg)
            else:
                return True
        return False


class Simple(Nullable):
    def __init__(
            self,
            *,
            coerce_to: typing.Optional[typing.Type] = None,
            fallback_coercion: bool = True,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('coerce_to', 'fallback_coercion'))
        self.coerce_to = coerce_to
        self.fallback_coercion = fallback_coercion

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        if self.coerce_to is not None:
            try:
                return self.coerce_to(value)
            except (ValueError, TypeError, AttributeError) as err:
                msg = f'could not coerce value {value!r} to {self.coerce_to!r}'
                raise exc.CoercionError(
                    msg,
                    coerced=self.coerce_to,
                    value=value,
                ) from err
        return value

    def check_type(
            self,
            value: typing.Any,
            expected_type: typing.Type,
            *,
            fallback: typing.Optional[typing.Any] = None,
    ) -> typing.Any:
        if not isinstance(value, expected_type):
            if self.fallback_coercion and fallback is not None:
                if callable(fallback):
                    value = fallback(value)
                else:
                    value = copy.deepcopy(fallback)
            else:
                msg = f'expected type {expected_type!r}; got value {value!r}'
                raise exc.InvalidTypeError(
                    msg,
                    expected=expected_type,
                    actual=type(value),
                )
        return value


def register(type_obj: typing.Type, validator: Validator) -> None:
    if type_obj in _validator_type_registry:
        msg = f'type {type_obj!r} already in validator registry'
        raise ValueError(msg)
    _validator_type_registry[type_obj] = validator


def get_validator(type_obj: typing.Type) -> typing.Type[Validator]:
    try:
        validator_type = _validator_type_registry[type_obj]
    except KeyError as err:
        msg = f'no validator for type {type_obj!r}'
        raise ValueError(msg) from err
    return validator_type
