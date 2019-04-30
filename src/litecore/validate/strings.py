import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc


class String(base.Simple):
    def __init__(
            self,
            *,
            length: typing.Optional[base.Length] = None,
            pattern: typing.Optional[base.Pattern] = None,
            one_of: typing.Optional[base.OneOf] = None,
            encoding: str = 'utf-8',
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params((
            'length',
            'pattern',
            'one_of',
            'encoding',
        ))
        self.length = length
        self.pattern = pattern
        self.one_of = one_of

    def _string_fallback(self, value: typing.Any) -> str:
        if isinstance(value, bytes):
            try:
                return value.decode(self.encoding)
            except (AttributeError, LookupError) as err:
                raise exc.StringDecodingError(
                    encoding=self.encoding,
                    value=value,
                ) from err
        msg = f'expected str; got value {value!r}'
        raise exc.InvalidTypeError(
            msg,
            expected=str,
            actual=type(value),
        )

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        value = super().detailed_validation(value)
        value = super().check_type(
            value,
            str,
            fallback=self._string_fallback,
        )
        if self.one_of is not None:
            value = self.one_of.validate(value)
        if self.length is not None:
            value = self.length.validate(value)
        if self.pattern is not None:
            value = self.pattern.validate(value)
        return value


base.register(str, String)
