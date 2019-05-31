import collections
import functools
import operator
import typing

from litecore import LitecoreError
import litecore.sentinels

_NO_VALUE = litecore.sentinels.NO_VALUE
_NO_ITEM_GETTER = litecore.sentinels.create('_NO_ITEM_GETTER')


class GetFieldError(LitecoreError, ValueError):
    pass


class GetColumnError(LitecoreError, ValueError):
    pass


def _check_strict(data, fields, attrs, items):
    if attrs is not _NO_VALUE and (items not in (_NO_VALUE, _NO_ITEM_GETTER)):
        msg = (
            f'data {data!r} has ambiguous attribute(s) and item(s) {fields!r} '
            f'with attribute value(s) {attrs!r} '
            f'and item value(s) {items!r}'
        )
        raise GetFieldError(msg)


def _get_field_helper(
    data: typing.Any,
    *,
    default: typing.Any = _NO_VALUE,
    strict: bool = False,
    _field: str,
    _attr_getter: typing.Callable,
    _item_getter: typing.Callable,
):
    try:
        item_value = _item_getter(data)
    except KeyError:
        item_value = _NO_VALUE
    except TypeError:
        item_value = _NO_ITEM_GETTER
    try:
        attr_value = _attr_getter(data)
    except AttributeError:
        attr_value = _NO_VALUE
    if strict:
        _check_strict(data, _field, attr_value, item_value)
    elif attr_value is not _NO_VALUE:
        return attr_value
    elif item_value not in (_NO_VALUE, _NO_ITEM_GETTER):
        return item_value
    if default is not _NO_VALUE:
        return default
    msg = (
        f'data {data!r} does not have field {_field!r} '
        f'and no default value provided'
    )
    raise GetFieldError(msg)


def _get_single_field(
    data: typing.Any,
    field: str,
    default: typing.Any,
    getter: typing.Callable[[str], typing.Any],
):
    try:
        return getter(data)
    except (AttributeError, KeyError):
        return default


def _get_multiple_fields_helper(
    data: typing.Any,
    *,
    default: typing.Any = _NO_VALUE,
    strict: bool = False,
    _all_attr_getter: typing.Callable,
    _all_item_getter: typing.Callable,
    _attr_getters: typing.Mapping[str, typing.Callable],
    _item_getters: typing.Mapping[str, typing.Callable],
):
    fields = tuple(_attr_getters.keys())
    try:
        item_values = _all_item_getter(data)
    except KeyError:
        item_values = _NO_VALUE
    except TypeError:
        item_values = _NO_ITEM_GETTER
    try:
        attr_values = _all_attr_getter(data)
    except AttributeError:
        attr_values = _NO_VALUE
    if strict:
        _check_strict(data, fields, attr_values, item_values)
    elif attr_values is not _NO_VALUE:
        return attr_values
    elif item_values not in (_NO_VALUE, _NO_ITEM_GETTER):
        return item_values
    if default is not _NO_VALUE:
        getters = _attr_getters if item_values is _NO_ITEM_GETTER else _item_getters
        return tuple(
            _get_single_field(data, field, default, getter)
            for field, getter in getters.items()
        )
    msg = (
        f'data {data!r} does not have all fields {fields!r} '
        f'and no default value provided'
    )
    raise GetFieldError(msg)


def fieldgetter(
    *fields,
    default: typing.Any = _NO_VALUE,
    strict: typing.Optional[bool] = None,
    name: typing.Optional[str] = None,
    doc: typing.Optional[str] = None,
) -> functools.partial:
    """

    Examples:

    >>> import datetime as dt
    >>> dates = [
    ...     dt.datetime(2018, 12, 31, 23, 45),
    ...     dt.datetime(2019, 1, 1, 7, 50),
    ...     dt.datetime(2019, 1, 2, 13, 5),
    ...     dt.datetime(2019, 1, 3, 11, 25),
    ... ]
    >>> day = fieldgetter('day')
    >>> [day(date) for date in dates]
    [31, 1, 2, 3]
    >>> week = fieldgetter('week')
    >>> [week(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have field 'week' and no default value provided
    >>> [week(date, default=None) for date in dates]
    [None, None, None, None]
    >>> day_default = fieldgetter('day', 'week', default=None)
    >>> [day_default(date) for date in dates]
    [(31, None), (1, None), (2, None), (3, None)]
    >>> hr_min = fieldgetter('hour', 'minute')
    >>> [hr_min(date) for date in dates]
    [(23, 45), (7, 50), (13, 5), (11, 25)]
    >>> hr_min_sec = fieldgetter('hour', 'minute', 'millisecond')
    >>> [hr_min_sec(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have all fields ... and no default value provided
    >>> results = [hr_min_sec(date, default=None) for date in dates]
    >>> results
    [(23, 45, None), (7, 50, None), (13, 5, None), (11, 25, None)]
    >>> import pickle
    >>> new_hr_min_sec = pickle.loads(pickle.dumps(hr_min_sec))
    >>> [new_hr_min_sec(date, default=None) for date in dates] == results
    True

    """
    if len(fields) > 1:
        all_attr_getter = operator.attrgetter(*fields)
        all_item_getter = operator.itemgetter(*fields)
        attr_getters = collections.OrderedDict(
            (field, operator.attrgetter(field)) for field in fields
        )
        item_getters = collections.OrderedDict(
            (field, operator.itemgetter(field)) for field in fields
        )
        getter = functools.partial(
            _get_multiple_fields_helper,
            _all_attr_getter=all_attr_getter,
            _all_item_getter=all_item_getter,
            _attr_getters=attr_getters,
            _item_getters=item_getters,
        )
    elif fields:
        field = fields[0]
        attr_getter = operator.attrgetter(field)
        item_getter = operator.itemgetter(field)
        getter = functools.partial(
            _get_field_helper,
            _field=field,
            _attr_getter=attr_getter,
            _item_getter=item_getter,
        )
    else:
        raise ValueError(f'expected at least one field')
    if default is not _NO_VALUE:
        getter = functools.partial(getter, default=default)
    if strict is not None:
        getter = functools.partial(getter, strict=strict)
    if name is not None:
        getter.__name__ = name
    if doc is not None:
        getter.__doc__ = doc
    return getter


class _NamedTupleMaker:
    def __init__(self, name, fields, getter):
        self.name = name
        self.fields = fields
        self._getter = getter
        self._nt = collections.namedtuple(name, fields, rename=True)

    def __getstate__(self):
        return (self.name, self.fields, self._getter)

    def __setstate__(self, state):
        self.__init__(*state)

    def __call__(self, data, **kwargs):
        items = self._getter(data, **kwargs)
        try:
            iter(items)
        except TypeError:
            items = (items,)
        return self._nt._make(items)


def namedtuple_fieldgetter(
    *fields,
    class_name: typing.Optional[str] = None,
    **kwargs
) -> _NamedTupleMaker:
    """

    Examples:

    >>> import datetime as dt
    >>> dates = [
    ...     dt.datetime(2018, 12, 31, 23, 45),
    ...     dt.datetime(2019, 1, 1, 7, 50),
    ...     dt.datetime(2019, 1, 2, 13, 5),
    ...     dt.datetime(2019, 1, 3, 11, 25),
    ... ]
    >>> day = namedtuple_fieldgetter('day', class_name='Example')
    >>> [day(date) for date in dates]
    [Example(day=31), Example(day=1), Example(day=2), Example(day=3)]
    >>> week = namedtuple_fieldgetter('week', class_name='Example2')
    >>> [week(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have field 'week' and no default value provided
    >>> [week(date, default=None) for date in dates]
    [Example2(week=None), Example2(week=None), Example2(week=None), Example2(week=None)]
    >>> day_default = namedtuple_fieldgetter('day', 'week', default=None, class_name='Example3')
    >>> [day_default(date) for date in dates]
    [Example3(day=31, week=None), Example3(day=1, week=None), Example3(day=2, week=None), Example3(day=3, week=None)]
    >>> hr_min = namedtuple_fieldgetter('hour', 'minute', class_name='TimeExample')
    >>> [hr_min(date) for date in dates]
    [TimeExample(hour=23, minute=45), TimeExample(hour=7, minute=50), TimeExample(hour=13, minute=5), TimeExample(hour=11, minute=25)]
    >>> hr_min_sec = namedtuple_fieldgetter('hour', 'minute', 'millisecond', class_name='TimeExample2')
    >>> [hr_min_sec(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have all fields ... and no default value provided
    >>> results = [hr_min_sec(date, default=None) for date in dates]
    >>> results  # doctest: +ELLIPSIS
    [..., TimeExample2(hour=11, minute=25, millisecond=None)]
    >>> import pickle
    >>> new_hr_min_sec = pickle.loads(pickle.dumps(hr_min_sec))
    >>> [new_hr_min_sec(date, default=None) for date in dates] == results
    True

    """
    if not fields:
        raise ValueError(f'expected at least one field')
    if class_name is None:
        class_name = 'namedtuple_fieldgetter'
    getter = fieldgetter(*fields, **kwargs)
    return _NamedTupleMaker(class_name, fields, getter)


def _record_maker(data, *, _fields, _getter, factory=dict, **kwargs):
    items = _getter(data, **kwargs)
    try:
        iter(items)
    except TypeError:
        items = (items,)
    return factory((field, item) for field, item in zip(_fields, items))


def record_fieldgetter(
    *fields,
    factory: typing.Optional[typing.Type] = None,
    **kwargs
) -> functools.partial:
    """

    Examples:

    >>> import datetime as dt
    >>> dates = [
    ...     dt.datetime(2018, 12, 31, 23, 45),
    ...     dt.datetime(2019, 1, 1, 7, 50),
    ...     dt.datetime(2019, 1, 2, 13, 5),
    ...     dt.datetime(2019, 1, 3, 11, 25),
    ... ]
    >>> day = record_fieldgetter('day')
    >>> [day(date) for date in dates]
    [{'day': 31}, {'day': 1}, {'day': 2}, {'day': 3}]
    >>> week = record_fieldgetter('week')
    >>> [week(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have field 'week' and no default value provided
    >>> [week(date, default=None) for date in dates]
    [{'week': None}, {'week': None}, {'week': None}, {'week': None}]
    >>> day_default = record_fieldgetter('day', 'week', default=None)
    >>> import collections
    >>> [day_default(date, factory=collections.OrderedDict) for date in dates]  # doctest: +ELLIPSIS
    [OrderedDict([('day', 31), ('week', None)]), ..., OrderedDict([('day', 3), ('week', None)])]
    >>> hr_min = record_fieldgetter('hour', 'minute')
    >>> [hr_min(date) for date in dates]  # doctest: +ELLIPSIS
    [{'hour': 23, 'minute': 45}, ..., {'hour': 11, 'minute': 25}]
    >>> hr_min_sec = record_fieldgetter('hour', 'minute', 'millisecond')
    >>> [hr_min_sec(date) for date in dates]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    getters.GetFieldError: data ... does not have all fields ... and no default value provided
    >>> results = [hr_min_sec(date, default=None) for date in dates]
    >>> results  # doctest: +ELLIPSIS
    [..., {'hour': 11, 'minute': 25, 'millisecond': None}]
    >>> import pickle
    >>> new_hr_min_sec = pickle.loads(pickle.dumps(hr_min_sec))
    >>> [new_hr_min_sec(date, default=None) for date in dates] == results
    True

    """
    if not fields:
        raise ValueError(f'expected at least one field')
    getter = fieldgetter(*fields, **kwargs)
    getter = functools.partial(
        _record_maker,
        _fields=fields,
        _getter=getter,
        **kwargs,
    )
    if factory is not None:
        getter = functools.partial(getter, factory=factory)
    return getter
