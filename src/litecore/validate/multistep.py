import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc


class _MultiValidation(base.Validator):
    def __init__(self, *validations, **kwargs):
        if __debug__:
            if not validations:
                raise ValueError('no validations specified')
        super().__init__(**kwargs)
        self.register_params(('validations',))
        self.validations = validations


class All(_MultiValidation):
    def detailed_validation(self, value: typing.Any) -> typing.Any:
        for step, validation in enumerate(self.validations):
            try:
                value = validation.validate(value)
            except exc.ValidationError as err:
                msg = (
                    f'validation of {value!r} failed at step {step}'
                    f'of validations {self.validations!r}'
                )
                raise exc.ValidationError(
                    msg,
                    value=value,
                    from_exception=err,
                ) from err
        return value


class Any(_MultiValidation):
    def detailed_validation(self, value: typing.Any) -> typing.Any:
        errors = exc.ErrorSequence()
        for step, validation in enumerate(self.validations):
            try:
                return validation.validate(value)
            except exc.ValidationError as err:
                errors.append(err)
        assert errors
        msg = f'value {value!r} did not succeed for any of {self.validations!r}'
        raise exc.MultiValidationError(
            msg,
            value=value,
            top_level_errors=None,
            underlying_errors=errors,
            results=None,
        )


class OnlyOne(_MultiValidation):
    def detailed_validation(self, value: typing.Any) -> typing.Any:
        successes = {}
        for step, validation in enumerate(self.validations):
            try:
                value = validation.validate(value)
            except exc.ValidationError:
                continue
            else:
                successes[step] = validation
        if len(successes) > 1:
            steps = ', '.join(
                f'step {step} = {validation!r}'
                for step, validation in successes.items()
            )
            msg = (
                f'value {value!r} succeeded for {len(successes)} '
                f'validations; successes were {steps!r}'
            )
            raise exc.MultiValidationError(
                msg,
                value=value,
                top_level_errors=None,
                underlying_errors=None,
                results=None,
            )
        return value
