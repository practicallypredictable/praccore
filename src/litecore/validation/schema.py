import collections
import copy
import logging
import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc

log = logging.getLogger(__name__)


def _validate_mapping(schema, value, *, unknown_keys_hook, errors=None, _memo=None):
    if errors is None:
        errors = {}
    keys_seen = set()
    item_keys = []
    item_values = []
    for item_key, item_value in value.items():
        keys_seen.add(item_key)
        if item_key in schema:
            try:
                item_value = schema[item_key].validate(item_value)
            except exc.ValidationError as err:
                errors[item_key] = err
                item_value = exc.FailedMarker(item_value)
        else:
            try:
                new_key, new_value = unknown_keys_hook(
                    item_key,
                    item_value,
                )
            except KeyError:
                key_error = exc.ForbiddenKeyError(
                    schema=schema,
                    key=item_key,
                )
                errors[item_key] = key_error
                item_key = exc.FailedMarker(item_key)
            if new_key is None:
                continue
            else:
                item_key = new_key
                item_value = new_value
        item_keys.append(item_key)
        item_values.append(item_value)
    for schema_key, schema_value in schema.items():
        if schema_key in keys_seen:
            continue
        if isinstance(schema_value, OptionalKey):
            default = schema_value.default
            try:
                schema_value = schema_value.validator.validate(default)
            except exc.ValidationError as err:
                errors[schema_key] = err
                schema_value = exc.FailedMarker(schema_value)
            item_keys.append(schema_key)
            item_values.append(schema_value)
        else:
            key_error = exc.MissingKeyError(
                schema=schema,
                key=schema_key,
            )
            errors[schema_key] = key_error
    assert len(item_keys) == len(item_values)
    return zip(item_keys, item_values), errors


class OptionalKey(base.Validator):
    def __init__(
            self,
            validator,
            *,
            default: typing.Optional[typing.Any] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._register_params((
            'validator',
            'default',
        ))
        self.validator = validator
        if default is not None and not callable(default):
            default = copy.deepcopy(default)
        self._default = default

    @property
    def default(self) -> typing.Any:
        if callable(self._default):
            return self._default()
        else:
            return self._default

    def preemptive_validation(self, value: typing.Any) -> bool:
        return self.validator.preemptive_validation(value)

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        return self.validator.detailed_validation(value)


def forbid_unknown_keys(key: typing.Hashable, value: typing.Any):
    raise KeyError()


def include_unknown_keys(key: typing.Hashable, value: typing.Any):
    return key, value


def exclude_unknown_keys(key: typing.Hashable, value: typing.Any):
    return None, None


class Schema(base.Nullable):
    def __init__(
            self,
            schema: typing.Mapping,
            *,
            unknown_keys_hook: typing.Callable = forbid_unknown_keys,
            mapping_factory: typing.Type = dict,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._register_params((
            'schema',
            'unknown_keys_hook',
            'mapping_factory',
        ))
        self.schema = schema
        self.unknown_keys_hook = unknown_keys_hook
        self.mapping_factory = mapping_factory

    def preemptive_validation(self, value: typing.Any) -> bool:
        if super().preemptive_validation(value):
            return value
        if not isinstance(value, collections.abc.Mapping):
            raise exc.InvalidTypeError(
                expected=collections.abc.Mapping,
                actual=type(value),
            )
        return False

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        top_level_errors = []
        errors = {}
        keys_seen = set()
        item_keys = []
        item_values = []
        for item_key, item_value in value.items():
            keys_seen.add(item_key)
            if item_key in self.schema:
                try:
                    item_value = self.schema[item_key].validate(item_value)
                except exc.ValidationError as err:
                    errors[item_key] = err
                    item_value = exc.FailedMarker(item_value)
            else:
                try:
                    new_key, new_value = self.unknown_keys_hook(
                        item_key,
                        item_value,
                    )
                except KeyError:
                    key_error = exc.ForbiddenKeyError(
                        schema=self.schema,
                        key=item_key,
                    )
                    errors[item_key] = key_error
                    item_key = exc.FailedMarker(item_key)
                if new_key is None:
                    continue
                else:
                    item_key = new_key
                    item_value = new_value
            item_keys.append(item_key)
            item_values.append(item_value)
        for schema_key, schema_value in self.schema.items():
            if schema_key in keys_seen:
                continue
            if isinstance(schema_value, OptionalKey):
                default = schema_value.default
                try:
                    schema_value = schema_value.validator.validate(default)
                except exc.ValidationError as err:
                    errors[schema_key] = err
                    schema_value = exc.FailedMarker(schema_value)
                item_keys.append(schema_key)
                item_values.append(schema_value)
            else:
                key_error = exc.MissingKeyError(
                    schema=self.schema,
                    key=schema_key,
                )
                errors[schema_key] = key_error
        assert len(item_keys) == len(item_values)
        results = self.mapping_factory(zip(item_keys, item_values))
        if errors or top_level_errors:
            raise exc.MultiValidationError(
                value=value,
                top_level_errors=top_level_errors,
                underlying_errors=errors,
                results=results,
            )
        return results
