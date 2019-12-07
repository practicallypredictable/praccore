import collections.abc
import functools

from typing import (
    Any,
    Callable,
    Mapping,
    Sequence,
    Type,
    Union,
)

import litecore.validation.base as base
import litecore.validation.length as length
import litecore.validation.exceptions as exc

TemplateType = Union[base.Validator, Type, Callable[[Any], Any]]


def _validate_template_value(template: Callable[[Any], Any], value: Any) -> Any:
    return template(value)


def _validate_template_type(template: Type, value: Any) -> Any:
    if not isinstance(value, template):
        raise exc.SimpleTypeError(value, template)
    return value


@base.abstractslots(base.combine_slots(
    length.HasLength,
    base.Nullable,
    base.Validator,
) + ('template', '_validate_template',))
class Collection(length.HasLength, base.Nullable, base.Validator):
    __slots__ = ()

    def __init__(
            self,
            *,
            template: TemplateType,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if not callable(template):
            raise TypeError('template must be callable')
        self.template = template
        if isinstance(self.template, type):
            func = _validate_template_type
        else:
            func = _validate_template_value
        self._validate_template = functools.partial(
            func,
            self.template,
        )


class Sequence(Collection):
    """

    Examples:

    >>> from numeric import Integer
    >>> template = Integer(min_value=0, max_value=10)
    >>> v = Sequence(template=template, min_length=2, max_length=4)
    >>> v('fail')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ContainerTypeError: value 'fail' type <class 'str'> rejected ...)
    >>> v([1, 2, 3, 's', 5])  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...MaxLengthError: value [1, 2, 3, 's', 5] has length 5 > bound 4
    >>> v([-2, 's', 7 ,11])  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore...ContainerValidationError: value [-2, 's', 7, 11] rejected ... with 3 error(s)...]
    >>> v([2.0, 0, 10, 8])
    [2, 0, 10, 8]
    >>> v([9])
    Traceback (most recent call last):
     ...
    litecore.validation.exceptions.MinLengthError: value [9] has length 1 < bound 2

    """
    __slots__ = base.get_slots(Collection) + ('unique', 'result_factory',)

    def __init__(
            self,
            *,
            unique: bool = False,
            result_factory: Type[Sequence] = list,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.unique = bool(unique)
        self.result_factory = result_factory

    def _validate_items(self, value: Any) -> Any:
        results = []
        errors = []
        if self.unique:
            hashable_seen = set()
            saw_hashable = hashable_seen.add
            unhashable_seen = []
            saw_unhashable = unhashable_seen.append
        for index, item in enumerate(value):
            caught_err = None
            try:
                item = self._validate_template(item)
            except exc.ValidationValueError as err:
                caught_err = exc.ContainerItemValueError(item, index, err)
            except exc.ValidationTypeError as err:
                caught_err = exc.ContainerItemTypeError(item, index, None, err)
            except exc.SimpleTypeError as err:
                caught_err = err
            if caught_err is not None:
                errors.append(caught_err)
                continue
            if self.unique:
                if item in hashable_seen or item in unhashable_seen:
                    err = exc.NonUniqueContainerItemError(item, index)
                    errors.append(err)
                try:
                    saw_hashable(item)
                except TypeError:
                    saw_unhashable(item)
            results.append(item)
        if not errors:
            if not isinstance(results, self.result_factory):
                results = self.result_factory(results)
            return results
        else:
            raise exc.ContainerValidationError(value, self, errors)

    def _validate(self, value: Any) -> Any:
        if isinstance(value, (str, bytes, bytearray)) or (
                not isinstance(value, collections.abc.Sequence)):
            raise exc.ContainerTypeError(value, self)
        results = self._validate_items(value)
        return super()._validate(results)


class Mapping(Collection):
    __slots__ = base.get_slots(Collection) + (
        'key_template',
        '_validate_key_template',
        'result_factory',
    )

    def __init__(
            self,
            *,
            key_template: TemplateType = str,
            result_factory: Type[Mapping] = dict,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.result_factory = result_factory
        self.key_template = key_template
        if isinstance(self.key_template, type):
            func = _validate_template_type
        else:
            func = _validate_template_value
        self._validate_key_template = functools.partial(
            func,
            self.key_template,
        )

    def _validate_items(self, value: Any) -> Any:
        results = []
        errors = []
        for item_key, item_value in value.items():
            caught_key_err = None
            caught_value_err = None
            try:
                item_key = self._validate_key_template(item_key)
            except exc.ValidationError as err:
                caught_key_err = exc.ContainerItemKeyError(
                    item_value, item_key, err)
            if caught_key_err is not None:
                errors.append(caught_key_err)
            try:
                item_value = self._validate_template(item_value)
            except exc.ValidationValueError as err:
                caught_value_err = exc.ContainerItemValueError(
                    item_value, item_key, err)
            except exc.ValidationTypeError as err:
                caught_value_err = exc.ContainerItemTypeError(
                    item_value, item_key, None, err)
            except exc.SimpleTypeError as err:
                caught_value_err = err
            if caught_value_err is not None:
                errors.append(caught_value_err)
            if caught_key_err or caught_value_err:
                continue
            results.append((item_key, item_value))
        if not errors:
            results = self.result_factory(results)
            return results
        else:
            raise exc.ContainerValidationError(value, self, errors)

    def _validate(self, value: Any) -> Any:
        if not isinstance(value, collections.abc.Mapping):
            raise exc.ContainerTypeError(value, self)
        results = self._validate_items(value)
        return super()._validate(results)
