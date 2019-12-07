import abc
import itertools
import math
import operator

from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

import litecore.validation.exceptions as exc

ValidatorType = TypeVar('ValidatorType', bound='Validator')

_abstract_slots: Dict[Type[ValidatorType], Tuple[str, ...]] = {}
register_slots = _abstract_slots.__setitem__
get_slots = _abstract_slots.__getitem__


def combine_slots(*classes) -> Tuple[str, ...]:
    slots = itertools.chain.from_iterable(
        get_slots(cls) for cls in classes)
    return tuple(slots)


def abstractslots(slots: Tuple[str, ...] = ()):
    def decorator(cls):
        register_slots(cls, slots)
        return cls
    return decorator


@abstractslots(('hook',))
class Validator(abc.ABC):
    __slots__ = ()

    def __init__(
            self,
            *,
            hook: Optional[Callable[[Any], Any]] = None,
            **kwargs,
    ):
        if hook is not None and not callable(hook):
            raise TypeError('hook must be callable')
        super().__init__(**kwargs)
        self.hook = hook

    @abc.abstractmethod
    def _validate(self, value: Any) -> Any:
        if self.hook is not None:
            try:
                value = self.hook(value)
            except Exception as err:
                raise exc.ExtraValidationError(value, self, err) from err
        return value

    def __call__(self, value: Any):
        return self._validate(value)

    @property
    def params(self) -> Tuple[str, ...]:
        return tuple(
            slot for slot in type(self).__slots__
            if not slot.startswith('_')
        )

    @property
    def param_items(self) -> Tuple[Tuple[str, Any], ...]:
        items = ((item, getattr(self, item)) for item in self.params)
        return tuple(items)

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in self.param_items)
        return f'{type(self).__name__}({params})'

    def __eq__(self, other: ValidatorType):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.param_items == other.param_items

    def __hash__(self):
        return hash((type(self).__name__, self.param_items))

    def clone(self, **kwargs) -> ValidatorType:
        params = dict(self.param_items)
        params.update(kwargs)
        return type(self)(**params)


class Anything(Validator):
    """Accepts any value.

    Examples:

    >>> validator = Anything()
    >>> validator
    Anything(hook=None)
    >>> validator(None)
    >>> validator(0)
    0
    >>> validator('test')
    'test'

    """
    __slots__ = get_slots(Validator)

    def _validate(self, value: Any) -> None:
        return super()._validate(value)


class Constant(Validator):
    """Rejects values other than a single specified value.

    Examples:

    >>> validator = Constant(value=42)
    >>> validator
    Constant(hook=None, value=42)
    >>> validator(42)
    42
    >>> validator(None)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ConstantError: value must equal 42; got None
    >>> validator(0)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ConstantError: value must equal 42; got 0
    >>> validator('test')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ConstantError: value must equal 42; got 'test'

    """
    __slots__ = get_slots(Validator) + ('value',)

    def __init__(self, *, value: Any, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def _validate(self, value: Any) -> Any:
        if value != self.value:
            raise exc.ConstantError(value, self)
        return super()._validate(value)


class Between(Validator):
    """Rejects values outside of specified bounds.

    Bounds can be non-numeric (e.g., strings), as long as the standard
    comparison operators work.

    Examples:

    >>> validator = Between(lower=10, upper=30)
    >>> validator
    Between(hook=None, lower=10, upper=30, lower_inclusive=True, upper_inclusive=True)
    >>> validator(9.99)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.LowerBoundError: value 9.99 not >= lower bound 10
    >>> validator(10)
    10
    >>> validator(25.5)
    25.5
    >>> validator(30)
    30
    >>> validator(42)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.UpperBoundError: value 42 not <= upper bound 30
    >>> validator(None)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value None incompatible with <class 'int'> ...
    >>> validator(float('inf'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.UpperBoundError: value inf not <= upper bound 30
    >>> validator(float('-inf'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.LowerBoundError: value -inf not >= lower bound 10
    >>> validator(float('nan'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...NaNError: value nan rejected by validator ...
    >>> validator('42')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ValidationTypeError: value '42' incompatible with <class 'int'> ...
    >>> first_half_alphabet = Between(lower='A', upper='M')
    >>> first_half_alphabet('B')
    'B'
    >>> first_half_alphabet('P')
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.UpperBoundError: value 'P' not <= upper bound 'M'
    >>> v2 = Between(lower=10, lower_inclusive=False)
    >>> v2(10)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.LowerBoundError: value 10 not > lower bound 10
    >>> v2(float('inf'))
    inf
    >>> v2(float('nan'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...NaNError: value nan rejected by validator ...
    >>> v3 = Between(upper=30, upper_inclusive=False)
    >>> v3(30)
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.UpperBoundError: value 30 not < upper bound 30
    >>> v3(float('-inf'))
    -inf
    >>> v3(float('nan'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...NaNError: value nan rejected by validator ...

    """
    __slots__ = get_slots(Validator) + (
        'lower',
        'upper',
        'lower_inclusive',
        'upper_inclusive',
        '_fail_lower',
        '_fail_upper',
    )

    def __init__(
        self,
        *,
        lower: Optional[Any] = None,
        upper: Optional[Any] = None,
        lower_inclusive: bool = True,
        upper_inclusive: bool = True,
        **kwargs,
    ) -> None:
        if lower is not None and upper is not None:
            try:
                valid = upper > lower
            except Exception as err:
                msg = f'upper and lower bounds must support comparison'
                raise TypeError(msg) from err
            if not valid:
                msg = f'upper bound must be greater than lower bound'
                raise ValueError(msg)
        super().__init__(**kwargs)
        self.lower = lower
        self.upper = upper
        self.lower_inclusive = bool(lower_inclusive)
        self.upper_inclusive = bool(upper_inclusive)
        if lower is not None:
            self._fail_lower = operator.lt if lower_inclusive else operator.le
        else:
            self._fail_lower = None
        if upper is not None:
            self._fail_upper = operator.gt if upper_inclusive else operator.ge
        else:
            self._fail_upper = None

    def _validate(self, value: Any) -> Any:
        try:
            if math.isnan(value):
                raise exc.NaNError(value, self)
        except TypeError:
            pass
        if self._fail_lower is not None:
            try:
                fail = self._fail_lower(value, self.lower)
            except TypeError as err:
                raise exc.ValidationTypeError(value, self, type(self.lower), err)
            if fail:
                raise exc.LowerBoundError(value, self)
        if self._fail_upper is not None:
            try:
                fail = self._fail_upper(value, self.upper)
            except TypeError as err:
                raise exc.ValidationTypeError(value, self, type(self.upper), err)
            if fail:
                raise exc.UpperBoundError(value, self)
        return super()._validate(value)


@abstractslots(('nullable',))
class Nullable(Validator):
    """Abstract base class for nullable validators.

    For a validator to be both Nullable and Coerceable, Nullable should
    come BEFORE Coerceable in the class declaration.

    """
    __slots__ = ()

    def __init__(
            self,
            *,
            nullable: bool = False,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.nullable = bool(nullable)

    def __call__(self, value: Any):
        if value is None and self.nullable:
            return value
        return super().__call__(value)


@abstractslots(('coerce', 'coerce_type',))
class Coerceable(Validator):
    """Abstract base class for validators allowing coercion.

    """
    __slots__ = ()
    default_coerce_type: ClassVar[Optional[Type]] = None

    def __init__(
            self,
            *,
            coerce: bool = False,
            coerce_type: Optional[Type] = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.coerce = bool(coerce)
        self.coerce_type = coerce_type or type(self).default_coerce_type
        if self.coerce and self.coerce_type is None:
            msg = f'validator {self!r} has no coercion type set'
            raise ValueError(msg)

    def _coerce_value(self, value: Any) -> Any:
        try:
            return self.coerce_type(value)
        except (TypeError, ValueError) as err:
            raise exc.CoercionError(value, self, self.coerce_type, err) from err

    def __call__(self, value: Any):
        try:
            value = self._validate(value)
        except exc.ValidationError:
            if not self.coerce:
                raise
        if self.coerce and not isinstance(value, self.coerce_type):
            value = self._coerce_value(value)
        return value


@abstractslots(('min_value', 'max_value',))
class HasBounds(Validator):
    """Rejects values falling outside a specified range.

    """
    __slots__ = ()

    def __init__(
        self,
        *,
        between: Optional[Between] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.between = between

    @abc.abstractmethod
    def _validate(self, value: Any) -> Any:
        if self.between is not None:
            value = self.between(value)
        return super()._validate(value)


@abstractslots(combine_slots(Nullable, Coerceable, Validator))
class Simple(Nullable, Coerceable, Validator):
    __slots__ = ()
