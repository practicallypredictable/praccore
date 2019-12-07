import abc
import enum

from typing import (
    Any,
    Hashable,
    Iterable,
    Optional,
    Set,
)

import litecore.validation.base as base
import litecore.validation.exceptions as exc


def _validate_choices(values: Iterable[Hashable]) -> Set[Hashable]:
    values = set(values)
    if not values:
        msg = f'must provide at least one value'
        raise ValueError(msg)
    return values


def _validate_enumerated_choices(values: enum.Enum) -> enum.Enum:
    if not issubclass(values, enum.Enum):
        msg = f'expected an enum; got {values!r}'
        raise TypeError(msg)
    return values


@base.abstractslots(base.get_slots(base.Validator) + ('values',))
class SpecifiedValueValidator(base.Validator):
    __slots__ = ()
    _validate_values = None

    def __init__(
        self,
        *,
        values: Iterable[Hashable],
        **kwargs,
    ) -> None:
        type(self)._validate_values(values)
        super().__init__(**kwargs)
        self.values = values


@base.abstractslots(base.get_slots(SpecifiedValueValidator))
class IncludedValueValidator(SpecifiedValueValidator):
    __slots__ = ()


class Choices(IncludedValueValidator):
    """Only accepts one of several possible specified values.

    Examples:

    >>> validator = Choices(values=set(['Alice', 'Bob', 'Charlie']))
    >>> validator('Alice')
    'Alice'
    >>> validator(2)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ChoiceError: invalid value 2; must be in ['Alice', 'Bob', 'Charlie']
    >>> validator(('Bob',))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ChoiceError: invalid value ('Bob',); ...
    >>> validator('David')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ChoiceError: invalid value 'David'; ...

    """
    __slots__ = base.get_slots(IncludedValueValidator)
    _validate_values = _validate_choices

    def _validate(self, value: Any) -> Any:
        if value not in self.values:
            raise exc.ChoiceError(value, self)
        return value


class EnumeratedChoices(IncludedValueValidator):
    """Only accepts one of several possible specified values.

    An alternative to Choices in which the allowed values are
    specified using an Enum from the standard library enum module.

    Values which correspond to an Enum member name or an Enum member
    value will pass validation. If a member name and member value
    collide, the validation will find the member name first. Therefore,
    as always it is good practice to use standard Python convention
    of using UPPER_CASE member names to distinguish them from values.

    Examples:

    >>> import enum
    >>> Colors = enum.Enum('Colors', [('CYAN', 4), ('MAGENTA', 5), ('YELLOW', 6)])
    >>> validator = EnumeratedChoices(values=Colors)
    >>> validator('CYAN')
    4
    >>> validator(4)
    4
    >>> validator('RED')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...EnumeratedChoiceError: invalid value 'RED'; must be in [..., <Colors.YELLOW: 6>]
    >>> validator(7)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...EnumeratedChoiceError: invalid value 7; must be in [..., <Colors.YELLOW: 6>]

    """
    __slots__ = base.get_slots(IncludedValueValidator)
    _validate_values = _validate_enumerated_choices

    def _validate(self, value: Any) -> Any:
        try:
            return self.values[value].value
        except KeyError:
            pass
        try:
            return self.values(value).value
        except ValueError:
            pass
        raise exc.EnumeratedChoiceError(value, self)


@base.abstractslots(base.get_slots(SpecifiedValueValidator))
class ExcludedValueValidator(SpecifiedValueValidator):
    __slots__ = ()


class Excluded(ExcludedValueValidator):
    """Rejects a value equal to one of several specified values.

    Examples:

    """
    __slots__ = base.get_slots(ExcludedValueValidator)
    _validate_values = _validate_choices

    def _validate(self, value: Any) -> Any:
        if value in self.values:
            raise exc.ExcludedChoiceError(value, self)
        return value


class EnumeratedExcluded(ExcludedValueValidator):
    __slots__ = base.get_slots(ExcludedValueValidator)
    _validate_values = _validate_enumerated_choices

    def _validate(self, value: Any) -> Any:
        if value in self.values:
            raise exc.ExcludedEnumeratedChoiceError(value, self)
        try:
            _ = self.values(value)
        except ValueError:
            pass
        else:
            raise exc.ExcludedEnumeratedChoiceError(value, self)
        return value


@base.abstractslots(('choices',))
class HasChoices(base.Validator):
    """Abstract base class for validators constrained to choices.

    """
    __slots__ = ()

    def __init__(
        self,
        *,
        choices: Optional[SpecifiedValueValidator] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.choices = choices

    @abc.abstractmethod
    def _validate(self, value: Any) -> Any:
        if self.choices is not None:
            value = self.choices(value)
        return super()._validate(value)


@base.abstractslots(base.combine_slots(HasChoices, base.Simple))
class SimpleChoices(HasChoices, base.Simple):
    __slots__ = ()
