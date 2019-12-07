from typing import (
    Any,
    Optional,
)

import litecore.validation.base as base
import litecore.validation.exceptions as exc


class Length(base.Validator):
    __slots__ = base.get_slots(base.Validator) + (
        'exactly',
        'at_least',
        'at_most',
        '_validator',
    )

    def __init__(
        self,
        *,
        exactly: Optional[int] = None,
        at_least: Optional[int] = None,
        at_most: Optional[int] = None,
        **kwargs,
    ) -> None:
        if exactly is not None and any((at_least, at_most)):
            msg = f'if exact length is specified, omit at least/at most'
            raise ValueError(msg)
        if exactly is not None:
            exactly = self._check_arg(exactly)
        if at_least is not None:
            at_least = self._check_arg(at_least)
        if at_most is not None:
            at_most = self._check_arg(at_most)
            if at_least is not None and at_least >= at_most:
                msg = f'at least should be less than at most'
                raise ValueError(msg)
        super().__init__(**kwargs)
        self.exactly = exactly
        self.at_least = at_least
        self.at_most = at_most
        if exactly is not None:
            self._validator = base.Constant(value=exactly)
        else:
            self._validator = base.Between(lower=at_least, upper=at_most)

        def _check_arg(self, arg) -> int:
            orig = arg
            try:
                arg = int(arg)
            except Exception as err:
                msg = f'{orig!r} cannot be interpreted as an integer'
                raise TypeError(msg) from err
            if arg != orig:
                msg = f'{orig!r} is not integral'
                raise ValueError(msg)
            if arg < 0:
                msg = f'lengths cannot be negative'
                raise ValueError(msg)
            return arg

    def _validate(self, value: Any) -> Any:
        try:
            len(value)
        except TypeError as err:
            msg = f'{value!r} has no len()'
            args = (value, self, None, err, msg)
            raise exc.ValidationTypeError(*args) from err
        try:
            self._validator(value)
        except exc.LowerBoundError:
            raise exc.MinLengthError(value, self)
        except exc.UpperBoundError:
            raise exc.MaxLengthError(value, self)
        except exc.ConstantError:
            raise exc.LengthError(value, self)
        return super()._validate(value)


@base.abstractslots(('length',))
class HasLength(base.Validator):
    """Must come FIRST
    """
    __slots__ = ()

    def __init__(
        self,
        *,
        length: Optional[Length] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.length = length

    def __call__(self, value: Any):
        if self.length is not None:
            value = self.length(value)
        return super().__call__(value)
