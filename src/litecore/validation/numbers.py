import decimal
import fractions
import math
import numbers
import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc


class Number(base.Simple):
    def __init__(
            self,
            *,
            bounds: typing.Optional[base.Range] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('bounds',))
        self.bounds = bounds


class Integer(Number):
    def __init__(
            self,
            *,
            one_of: typing.Optional[base.OneOf] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('one_of',))
        self.one_of = one_of

    def _integer_fallback(self, value: typing.Any) -> int:
        if isinstance(value, float) and value.is_integer():
            return int(value)
        else:
            try:
                as_int = int(value)
            except (ValueError, TypeError) as err:
                raise exc.CoercionError(
                    coerced=int,
                    value=value,
                ) from err
        if as_int == value:
            return as_int
        else:
            msg = f'expected integral type; got value {value!r}'
            raise exc.InvalidTypeError(
                msg,
                expected=numbers.Integral,
                actual=type(value),
            )

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        value = super().detailed_validation(value)
        value = super().check_type(
            value,
            numbers.Integral,
            fallback=self._integer_fallback,
        )
        if self.one_of is not None:
            value = self.one_of.validate(value)
        if self.bounds is not None:
            value = self.bounds.validate(value)
        return value


class Fraction(Number):
    def __init__(
            self,
            *,
            one_of: typing.Optional[base.OneOf] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('one_of',))
        self.one_of = one_of

    def _rational_fallback(self, value: typing.Any) -> fractions.Fraction:
        if isinstance(value, float):
            return fractions.Fraction.from_float(value)
        elif isinstance(value, decimal.Decimal):
            return fractions.Fraction.from_decimal(value)
        else:
            try:
                return fractions.Fraction(value)
            except TypeError as err:
                raise exc.CoercionError(
                    coerced=int,
                    value=value,
                ) from err
        msg = f'expected rational type; got value {value!r}'
        raise exc.InvalidTypeError(
            msg,
            expected=numbers.Rational,
            actual=type(value),
        )

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        value = super().detailed_validation(value)
        value = super().check_type(
            value,
            numbers.Rational,
            fallback=self._rational_fallback,
        )
        if self.one_of is not None:
            value = self.one_of.validate(value)
        if self.bounds is not None:
            value = self.bounds.validate(value)
        return value


class Float(Number):
    def __init__(
            self,
            *,
            nan_ok: bool = False,
            inf_ok: bool = False,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params(('nan_ok', 'inf_ok'))
        self.nan_ok = nan_ok
        self.nan_ok = inf_ok

    def _float_fallback(self, value: typing.Any) -> float:
        # TODO: any other types? decimal/fraction already covered by Real
        msg = f'expected float; got value {value!r}'
        raise exc.InvalidTypeError(
            msg,
            expected=numbers.Real,
            actual=type(value),
        )

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        value = super().detailed_validation(value)
        value = super().check_type(
            value,
            numbers.Real,
            fallback=self._float_fallback,
        )
        # TODO: does this work if not coerced?
        if math.isnan(value) and not self.nan_ok:
            msg = f'value cannot be a NaN; got {value!r}'
            raise exc.InvalidValueError(msg)
        if math.isinf(value) and not self.inf_ok:
            msg = f'value cannot be infinite; got {value!r}'
            raise exc.InvalidValueError(msg)
        if self.bounds is not None:
            value = self.bounds.validate(value)
        return value


base.register(int, Integer)
base.register(fractions.Fraction, Fraction)
base.register(float, Float)
# TODO: decimal
