import collections
import logging
import typing

import litecore.validate.base as base
import litecore.validate.exceptions as exc

log = logging.getLogger(__name__)


class Tuple(base.Nullable):
    def __init__(
            self,
            *items,
            tuple_factory: typing.Type = tuple,
            **kwargs,
    ) -> None:
        if __debug__:
            if not items:
                msg = f'must provide at least one item validator'
                raise ValueError(msg)
        super().__init__(**kwargs)
        self.register_params(('items', 'tuple_factory'))
        self.items = items
        self.tuple_factory = tuple_factory

    def preemptive_validation(self, value: typing.Any) -> bool:
        if super().preemptive_validation(value):
            return value
        if (isinstance(value, (str, bytes)) or not
                isinstance(value, collections.abc.Sequence)):
            raise exc.InvalidTypeError(
                expected=collections.abc.Sequence,
                actual=type(value),
            )
        length = len(self.items)
        if len(value) != length:
            raise exc.LengthError(
                constraint=length,
                value=value,
            )
        return False

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        errors = {}
        results = []
        for i, item in enumerate(value):
            try:
                item = self.items[i].validate(item)
            except exc.ValidationError as err:
                errors[i] = err
                results.append(exc.FailedMarker(item, index=i))
                continue
            else:
                results.append(item)
        if errors:
            raise exc.MultiValidationError(
                value=value,
                top_level_errors=None,
                underlying_errors=errors,
                results=results,
            )
        return self.tuple_factory(results)

# TODO: namedtuples, dataclasses, sets


class Sequence(base.Nullable):
    def __init__(
            self,
            validator: base.Validator,
            *,
            length: typing.Optional[base.Length] = None,
            sequence_factory: typing.Type = list,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_params((
            'validator',
            'length',
            'sequence_factory',
        ))
        self.validator = validator
        self.length = length
        self.sequence_factory = sequence_factory

    def preemptive_validation(self, value: typing.Any) -> bool:
        if super().preemptive_validation(value):
            return value
        if (isinstance(value, (str, bytes)) or not
                isinstance(value, collections.abc.Sequence)):
            raise exc.InvalidTypeError(
                expected=collections.abc.Sequence,
                actual=type(value),
            )
        return False

    def detailed_validation(self, value: typing.Any) -> typing.Any:
        errors = {}
        top_level_errors = []
        results = []
        for i, item in enumerate(value):
            try:
                item = self.validator.validate(item)
            except exc.ValidationError as err:
                errors[i] = err
                results.append(exc.FailedMarker(item, index=i))
                continue
            else:
                results.append(value)
        if self.length is not None:
            try:
                value = self.length.validate(value)
            except exc.LengthError as err:
                top_level_errors.append(err)
        if errors or top_level_errors:
            raise exc.MultiValidationError(
                value=value,
                top_level_errors=top_level_errors,
                underlying_errors=errors,
                results=results,
            )
        return self.sequence_factory(results)


# class Mapping(Nullable):
#     def __init__(
#             self,
#             *,
#             key_validator: Validator,
#             value_validator: Validator,
#             length: typing.Optional[Length] = None,
#             mapping_factory: typing.Type = dict,
#             **kwargs,
#     ) -> None:
#         super().__init__(**kwargs)
#         self._register_params((
#             'key_validator',
#             'value_validator',
#             'length',
#             'mapping_factory',
#         ))
#         self.key_validator = key_validator
#         self.value_validator = value_validator
#         self.length = length
#         self.mapping_factory = mapping_factory

#     def preemptive_validation(self, value: typing.Any) -> bool:
#         if super().preemptive_validation(value):
#             return value
#         if not isinstance(value, collections.abc.Mapping):
#             raise exc.InvalidTypeError(
#                 expected=collections.abc.Mapping,
#                 actual=type(value),
#             )
#         return False

#     def detailed_validation(self, value: typing.Any) -> typing.Any:
#         errors = collections.defaultdict(dict)
#         top_level_errors = []
#         item_keys = []
#         item_values = []
#         for item_key, item_value in value.items():
#             try:
#                 item_key = self.key_validator.validate(item_key)
#             except exc.ValidationError as err:
#                 msg = f'failed to validate key {item_key!r} from {value!r}'
#                 key_error = exc.InvalidKeyError(
#                     msg,
#                     key=item_key,
#                     from_exception=err,
#                 )
#                 errors[item_key]['key'] = key_error
#                 item_key = exc.FailedMarker(item_key)
#             item_keys.append(item_key)
#             try:
#                 item_value = self.value_validator.validate(item_value)
#             except exc.ValidationError as err:
#                 msg = f'failed to validate value {item_value!r} from {value!r}'
#                 value_error = exc.InvalidValueError(
#                     msg,
#                     value=item_value,
#                     from_exception=err,
#                 )
#                 errors[item_key]['value'] = value_error
#                 item_value = exc.FailedMarker(item_value)
#             item_values.append(item_value)
#         assert len(item_keys) == len(item_values)
#         if self.length is not None:
#             try:
#                 value = self.length.validate(value)
#             except exc.LengthError as err:
#                 top_level_errors.append(err)
#         if errors or top_level_errors:
#             raise exc.MultiValidationError(
#                 value=value,
#                 top_level_errors=top_level_errors,
#                 underlying_errors=errors,
#                 results=collections.OrderedDict(zip(item_keys, item_values)),
#             )
#         return self.mapping_factory(zip(item_keys, item_values))
