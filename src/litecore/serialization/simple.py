import functools
import logging

from typing import (
    Any,
    Dict,
    FrozenSet,
    Set,
)

import litecore.serialization.classes


def _encode(
        *,
        class_key: str = '__json__',
        class_name: str,
        data_key: str = '__data__',
        data: Any,
        factor:
) -> litecore.serialization.classes:
    # Be mindful of insertion order
    encoding = {class_key: class_name}
    encoding.update({data_key: data})
    return encoding


@functools.singledispatch
def to_json(obj, **kwargs) -> Dict[str, Any]:
    """Encode objects of various types to JSON.

    Decorated by functools.singledispatch to dispatch on the type of the object
    argument. See the registry property of functions decorated by
    functools.singledispatch to view the supported types and a mapping of types
    to the encoding functions.

    This framework defines encodings for a number of standard Python types:
        - set
        - frozenset
        - tuple
        - MappingProxyType
        - datetime, date, time, timedelta
        - Decimal
        - Fraction
        - complex

    NOTE: Currently, time and datetime are timezone-naive.

    The generic function raises TypeError to catch unrecognized types.

    """
    msg = f'Undispatched attempt to encode object of type {type(obj)}: {obj}'
    raise TypeError(msg)


@to_json.register(set)
def _(obj: set, **kwargs) -> Dict[str, Any]:
    return _encode(class_name='set', data=list(obj))


@register_json_decoder('set')
def _decode_set(*, data: JSONType) -> Set[Any]:
    return set(data)


@to_json.register(frozenset)
def _(obj: frozenset, **kwargs) -> Dict[str, Any]:
    return _encode(class_name='frozenset', data=list(obj))


@register_json_decoder('frozenset')
def _decode_frozenset(*, data: JSONType) -> FrozenSet[Any]:
    return frozenset(data)


@encode_json.register(set)
def _encode_tuple(obj: set, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(base_class_name='tuple', data=list(obj), **kwargs)


@register_json_decoder('tuple')
def _decode_tuple(*, data: JSONType) -> Tuple[Any]:
    return tuple(data)


@encode_json.register(types.MappingProxyType)
def _encode_mapping_proxy(
        obj: types.MappingProxyType, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='MappingProxyType',
        data=list(obj),
        **kwargs,
    )


@register_json_decoder('MappingProxyType')
def _decode_mapping_proxy(*, data: JSONType) -> types.MappingProxyType:
    return types.MappingProxyType(data)


@encode_json.register(Decimal)
def _encode_decimal(obj: Decimal, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(base_class_name='Decimal', data=str(obj), **kwargs)


@register_json_decoder('Decimal')
def _decode_decimal(*, data: str) -> Decimal:
    return Decimal(data)


@encode_json.register(Fraction)
def _encode_fraction(obj: Fraction, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(base_class_name='Fraction', data=str(obj), **kwargs)


@register_json_decoder('Fraction')
def _decode_fraction(*, data: str) -> Fraction:
    return Fraction(data)


@encode_json.register(complex)
def _encode_complex(obj: complex, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='complex',
        data={'_real': obj.real, '_imag': obj.imag},
        **kwargs,
    )


@register_json_decoder('complex')
def _decode_complex(*, data: JSONType) -> Fraction:
    return complex(data['_real'], data['_imag'])


@encode_json.register(dt.datetime)
def _encode_naive_datetime(obj: dt.datetime, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='naive-datetime',
        data=obj.strftime(NAIVE_DATETIME_FORMAT),
        **kwargs,
    )


@register_json_decoder('naive-datetime')
def _decode_naive_datetime(*, data: str) -> dt.datetime:
    return dt.datetime.strptime(data, NAIVE_DATETIME_FORMAT)


@encode_json.register(dt.date)
def _encode_date(obj: dt.date, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='date',
        data=obj.strftime(DATE_FORMAT),
        **kwargs,
    )


@register_json_decoder('date')
def _decode_date(*, data: str) -> dt.date:
    return dt.datetime.strptime(data, DATE_FORMAT).date()


@encode_json.register(dt.time)
def _encode_naive_time(obj: dt.time, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='naive-time',
        data=obj.strftime(NAIVE_TIME_FORMAT),
        **kwargs,
    )


@register_json_decoder('naive-time')
def _decode_naive_time(*, data: str) -> dt.time:
    return dt.datetime.strptime(data, NAIVE_TIME_FORMAT).time()


@encode_json.register(dt.timedelta)
def _encode_timedelta(obj: dt.timedelta, **kwargs) -> Dict[str, Any]:
    return _encode_as_json(
        base_class_name='timedelta',
        data={
            'days': obj.days,
            'seconds': obj.seconds,
            'microseconds': obj.microseconds,
        },
        **kwargs,
    )


@register_json_decoder('timedelta')
def _decode_timedelta(*, data: Mapping) -> dt.timedelta:
    return dt.timedelta(
        days=data['days'],
        seconds=data['seconds'],
        microseconds=data['microseconds'],
    )
