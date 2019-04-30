import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc

TRUE_CASEFOLDED_VALUES = ('true', 'yes', 'y', 'on')
FALSE_CASEFOLDED_VALUES = ('false', 'no', 'n', 'off')


class Boolean(base.Simple):
    def __init__(
            self,
            *,
            coerce_string: bool = False,
            true_strings=TRUE_CASEFOLDED_VALUES,
            false_strings=FALSE_CASEFOLDED_VALUES,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.register_params(('coerce_string',))
        self.coerce_string = coerce_string
        self._true_values = true_strings
        self._false_values = false_strings

    def _bool_fallback(self, value: typing.Any) -> bool:
        if isinstance(value, str) and self.coerce_string:
            value = value.casefold()
            if value in self._true_values:
                return True
            elif value in self._false_values:
                return False
            else:
                msg = f'cannot convert unrecognized value {value!r} to bool'
                raise exc.SpecifiedValueError(
                    msg,
                    constraint=self._true_values + self._false_values,
                    actual=value,
                )
        msg = f'expected bool; got value {value!r}'
        raise exc.InvalidTypeError(
            msg,
            expected=bool,
            actual=type(value),
        )

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        value = super().detailed_validation(value)
        value = super().check_type(
            value,
            bool,
            fallback=self._bool_fallback,
        )
        return value


base.register(bool, Boolean)
