from typing import (
    Any,
)

import litecore.validation.base as base
import litecore.validation.exceptions as exc


@base.abstractslots(('validations', 'fail_fast'))
class MultiValidator(base.Validator):
    __slots__ = ()

    def __init__(
            self,
            *validations,
            fail_fast: bool = True,
            **kwargs,
    ):
        if len(validations) < 1:
            raise ValueError('no validations specified')
        super().__init__(**kwargs)
        self.validations = validations
        self.fail_fast = bool(fail_fast)


class AllOf(MultiValidator):
    __slots__ = base.get_slots(MultiValidator)

    def _validate(self, value: Any) -> Any:
        errors = []
        for step, validation in enumerate(self.validations):
            try:
                value = validation(value)
            except exc.ValidationError as err:
                details = (step, err)
                if self.fail_fast:
                    raise exc.MultiStepValidationError(value, self, [details])
                errors.append(details)
        if errors:
            raise exc.MultiStepValidationError(value, self, errors)
        return value


class AnyOf(MultiValidator):
    __slots__ = base.get_slots(MultiValidator)

    def _validate(self, value: Any) -> Any:
        errors = []
        for step, validation in enumerate(self.validations):
            try:
                return validation(value)
            except exc.ValidationError as err:
                errors.append((step, err))
        raise exc.MultiStepValidationError(value, self, errors)


def _limit_successes(validator: MultiValidator, limit: int, value: Any) -> Any:
    successes = []
    for step, validation in enumerate(validator.validations):
        try:
            value = validation(value)
        except exc.ValidationError:
            continue
        successes.append((step, validation))
        if validator.fail_fast and len(successes) > limit:
            break
    if len(successes) > limit:
        msg = (
            f'{len(successes)} validations succeeded > limit {limit}; '
            f'following validations succeeded: {successes!r}'
        )
        raise exc.MultiStepValidationError(value, validator, successes, msg)
    return value


class OnlyOneOf(MultiValidator):
    __slots__ = base.get_slots(MultiValidator)

    def _validate(self, value: Any) -> Any:
        return _limit_successes(self, 1, value)


class NotAnyOf(MultiValidator):
    __slots__ = base.get_slots(MultiValidator)

    def _validate(self, value: Any) -> Any:
        return _limit_successes(self, 0, value)
