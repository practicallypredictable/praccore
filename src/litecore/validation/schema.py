import collections

from typing import (
    Any,
    Callable,
    Hashable,
    Mapping,
    NoReturn,
    Tuple,
    Type,
    Union,
)

import litecore.validation.base as base
import litecore.validation.exceptions as exc
import litecore.sentinels
import litecore.utils

NO_VALUE = litecore.sentinels.create('NO_VALUE')

default_factory = litecore.utils.constant_factory


class OptionalKey(base.Validator):
    __slots__ = base.get_slots(base.Validator) + (
        'validator',
        'default_factory',
    )

    def __init__(
            self,
            *,
            validator: base.ValidatorType,
            default_factory: Callable[[], Any],
            **kwargs,
    ):
        try:
            validator(default_factory())
        except Exception as err:
            msg = f'default factory value failed validation'
            raise RuntimeError(msg) from err
        super().__init__(**kwargs)
        self.validator = validator
        self.default_factory = default_factory

    @property
    def default(self) -> Any:
        return self.default_factory()

    def _validate(self, value: Any) -> Any:
        value = self.validator(value)
        return super()._validate(value)


UnknownKeyReturnType = Union[NoReturn, Tuple[str, Any], Tuple[None, None]]
UnknownKeyHook = Callable[[Tuple[str, Any]], UnknownKeyReturnType]


def raise_unknown_keys(key: str, value: Any) -> NoReturn:
    msg = f'key {key!r} with value {value!r} is forbidden'
    raise KeyError(msg)


def include_unknown_keys(key: str, value: Any) -> Tuple[str, Any]:
    return key, value


def exclude_unknown_keys(key: str, value: Any) -> Tuple[None, None]:
    return None, None


@base.abstractslots(base.combine_slots(base.Validator))
class Schema(base.Validator):
    __slots__ = ()


class MappingSchema(Schema):
    __slots__ = base.get_slots(Schema) + (
        'schema',
        'unknown_key_hook',
        'factory',
    )

    def __init__(
        self,
        *,
        schema: Mapping[str, Any],
        unknown_key_hook: UnknownKeyHook = raise_unknown_keys,
        factory: Type[Mapping] = dict,
        **kwargs,
    ):
        if not isinstance(schema, collections.abc.Mapping):
            raise TypeError()
        super().__init__(**kwargs)
        self.schema = schema

    def _validate(self, value: Mapping[Hashable, Any]) -> Mapping[Hashable, Any]:
        if not isinstance(value, collections.abc.Mapping):
            raise TypeError()
        keys_seen = set()
        saw = keys_seen.add
        validated = []
        for key, value in value.items():
            saw(key)
            if key not in self.schema:
                try:
                    key, value = self.unknown_keys_hook(key, value)
                except Exception as err:
                    raise exc.ValidationError() from err
                if key is None:
                    continue
            else:
                validator = self.schema[key]
                if isinstance(validator, base.Validator):
                    try:
                        value = validator(value)
                    except exc.ValidationError as err:
                        raise exc.ValidationError() from err
                elif isinstance(validator, type):
                    if not isinstance(value, validator):
                        raise exc.ValidationError()
                else:
                    if value != validator:
                        raise exc.ValidationError()
                validated.append((key, value))
        for key, validator in self.schema.items():
            if key in keys_seen:
                continue
            if isinstance(validator, OptionalKey):
                validated.append((key, validator.default))
            else:
                raise KeyError()
        return super()._validate(validated)
