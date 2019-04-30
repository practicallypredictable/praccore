import datetime as dt
import decimal
import fractions
import logging
import types

import litecore.serialize.asjson as asjson

log = logging.getLogger(__name__)

NAIVE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
NAIVE_TIME_FORMAT = '%H:%M:%S.%fZ'
DATE_FORMAT = '%Y-%m-%d'


def _as_str(obj):
    return str(obj)


def _as_list(obj):
    return list(obj)


def _as_dict(obj):
    return dict(obj)


asjson.register_type(tuple, 'builtins.tuple', _as_list)
asjson.register_type(set, 'builtins.set', _as_list)
asjson.register_type(frozenset, 'builtins.frozenset', _as_list)
asjson.register_type(types.MappingProxyType, 'types.MappingProxyType', _as_dict)
asjson.register_type(decimal.Decimal, 'decimal.Decimal', _as_str)
asjson.register_type(fractions.Fraction, 'fractions.Fraction', _as_str)


def _encode_range(obj):
    return {
        '__start__': obj.start,
        '__stop__': obj.stop,
        '__step__': obj.step,
    }


def _decode_range(data):
    return range(data['__start__'], data['__stop__'], data['__step__'])


asjson.register_type(range, 'builtin.range', _encode_range, _decode_range)


def _encode_bytes(obj):
    return obj.decode('utf-8')


def _decode_bytes(data):
    return str.encode(data, 'utf-8')


asjson.register_type(bytes, 'builtin.bytes', _encode_bytes, _decode_bytes)


def _encode_bytearray(obj):
    return obj.decode('utf-8')


def _decode_bytearray(data):
    return bytearray(data, 'utf-8')


asjson.register_type(
    bytearray,
    'builtin.bytearray',
    _encode_bytearray,
    _decode_bytearray,
)


def _encode_complex(obj):
    return {'__real__': obj.real, '__imag__': obj.imag}


def _decode_complex(data):
    return complex(data['__real__'], data['__imag__'])


asjson.register_type(
    complex,
    'builtins.complex',
    _encode_complex,
    _decode_complex,
)


def _encode_datetime(obj):
    return obj.strftime(NAIVE_DATETIME_FORMAT)


def _decode_datetime(data):
    return dt.datetime.strptime(data, NAIVE_DATETIME_FORMAT)


asjson.register_type(
    dt.datetime,
    'datetime.datetime-naive',
    _encode_datetime,
    _decode_datetime,
)


def _encode_date(obj):
    return obj.strftime(DATE_FORMAT)


def _decode_date(data):
    return dt.datetime.strptime(data, DATE_FORMAT).date()


asjson.register_type(
    dt.date,
    'datetime.date',
    _encode_date,
    _decode_date,
)


def _encode_time(obj):
    return obj.strftime(NAIVE_TIME_FORMAT)


def _decode_time(data):
    return dt.datetime.strptime(data, NAIVE_TIME_FORMAT).time()


asjson.register_type(
    dt.time,
    'datetime.time-naive',
    _encode_time,
    _decode_time,
)


def _encode_timedelta(obj):
    return {
        'days': obj.days,
        'seconds': obj.seconds,
        'microseconds': obj.microseconds
    }


def _decode_timedelta(data):
    return dt.timedelta(
        days=data['days'],
        seconds=data['seconds'],
        microseconds=data['microseconds'],
    )


asjson.register_type(
    dt.timedelta,
    'datetime.timedelta',
    _encode_timedelta,
    _decode_timedelta,
)
