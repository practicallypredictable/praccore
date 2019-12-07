import decimal
import fractions
import math
import numbers

from typing import (
    Any,
)

import litecore.validation.base as base
import litecore.validation.specified as specified
import litecore.validation.exceptions as exc


@base.abstractslots(
    base.combine_slots(
        base.HasBounds,
        specified.SimpleChoices,
    ) + ('coerce_implicit',)
)
class Numeric(base.HasBounds, specified.SimpleChoices):
    """Abstract base class for validating numeric values."""
    __slots__ = ()

    def __init__(
            self,
            *,
            coerce_implicit: bool = True,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.coerce_implicit = bool(coerce_implicit)


class Integer(Numeric):
    """

    Examples:

    >>> import fractions
    >>> import decimal
    >>> import enum
    >>> import pickle
    >>> import copy
    >>> f1 = fractions.Fraction(30, 10)
    >>> f2 = fractions.Fraction(30, 11)
    >>> d1 = decimal.Decimal('10.000')
    >>> d2 = decimal.Decimal('10.001')
    >>> betw10and30 = Integer(between=base.Between(lower=10, upper=30))
    >>> assert pickle.loads(pickle.dumps(betw10and30)) == betw10and30
    >>> c = copy.deepcopy(betw10and30)
    >>> assert c == betw10and30
    >>> betw10and30  # doctest: +ELLIPSIS
    Integer(..., min_value=-10, max_value=30, coerce_implicit_integer=True)
    >>> betw10and30_no_coerce = betw10and30.clone(coerce_implicit_integer=False)
    >>> assert pickle.loads(pickle.dumps(betw10and30_no_coerce)) == betw10and30_no_coerce
    >>> betw10and30_no_coerce  # doctest: +ELLIPSIS
    Integer(..., min_value=-10, max_value=30, coerce_implicit_integer=False)
    >>> int_v3 = Integer(min_value=3, choices=base.Choices(values=[2, 4, 6]))
    >>> EnumChoices = enum.Enum('EnumChoices', 'CAT DOG MOUSE')
    >>> assert EnumChoices.CAT.value == 1
    >>> int_v4 = Integer(coerce=True, choices=base.Enumerated(values=EnumChoices))
    >>> betw10and30(None)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> betw10and30(-11)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.LowerBoundError: value -11 < bound -10
    >>> betw10and30(-9)
    -9
    >>> betw10and30(-9.1)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> betw10and30(-9.0)
    -9
    >>> betw10and30(f1)
    3
    >>> betw10and30_no_coerce(f1)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> betw10and30(d1)
    10
    >>> betw10and30_no_coerce(d1)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> betw10and30(f2)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> betw10and30(d2)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> int_v3(4)
    4
    >>> int_v3(5)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.ChoiceError: value 5 is not an allowed choice
    >>> int_v3(2)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.LowerBoundError: value 2 < bound 3
    >>> int_v3('5')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value ... incompatible with <class 'numbers.Integral'>
    >>> int_v4('5')  # this validator tries explicit coercion to int
    5
    >>> int_v4('hi')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.CoercionError: value 'hi' incompatible with <class 'int'>

    """
    __slots__ = base.get_slots(Numeric)
    default_coerce_type = int

    def _validate(self, value: Any) -> Any:
        if not isinstance(value, numbers.Integral):
            if self.coerce_implicit:
                if isinstance(value, float) and value.is_integer():
                    return int(value)
                elif isinstance(value, fractions.Fraction):
                    if value.denominator == 1:
                        return int(value)
                elif isinstance(value, decimal.Decimal):
                    if value.as_integer_ratio()[1] == 1:
                        return int(value)
            raise exc.ValidationTypeError(value, self, numbers.Integral)
        return super()._validate(value)


class Fraction(Numeric):
    __slots__ = base.get_slots(Numeric)
    default_coerce_type = fractions.Fraction

    def _validate(self, value: Any) -> Any:
        if not isinstance(value, numbers.Rational):
            if self.coerce_implicit:
                if isinstance(value, float):
                    return fractions.Fraction.from_float(value)
                elif isinstance(value, decimal.Decimal):
                    return fractions.Fraction.from_decimal(value)
            raise exc.ValidationTypeError(value, self, numbers.Rational)
        return super()._validate(value)


class Float(Numeric):
    """

    """
    __slots__ = base.get_slots(Numeric) + (
        'nan_ok',
        'inf_ok',
    )
    default_coerce_type = float
    implicitly_coerceable = (
        numbers.Integral,
        fractions.Fraction,
        decimal.Decimal,
    )

    def __init__(
            self,
            *,
            nan_ok: bool = False,
            inf_ok: bool = False,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.nan_ok = bool(nan_ok)
        self.inf_ok = bool(inf_ok)

    def _validate(self, value: Any) -> Any:
        if not isinstance(value, numbers.Real):
            raise exc.ValidationTypeError(value, self, numbers.Real)
        if not isinstance(value, float):
            if self.coerce_implicit and (
                    isinstance(value, self.implicitly_coerceable)):
                return float(value)
        if math.isnan(value) and not self.nan_ok:
            raise exc.ValidationValueError(value, self)
        if math.isinf(value) and not self.inf_ok:
            raise exc.ValidationValueError(value, self)
        return super()._validate(value)
