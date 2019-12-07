import datetime as dt
import decimal
import fractions
import types

from typing import (
    Any,
    Dict,
    List,
)

import litecore.serialization.asjson.coding as coding

DEFAULT_BYTE_ENCODING = 'utf-8'
_byte_encoding = DEFAULT_BYTE_ENCODING


def set_byte_encoding(encoding: str = DEFAULT_BYTE_ENCODING) -> None:
    global _byte_encoding
    _byte_encoding = encoding


def get_byte_encoding() -> str:
    return _byte_encoding


def _decode_byte_objects(obj: Any) -> Dict[str, Any]:
    return {
        '__decoded__': obj.decode(_byte_encoding),
        '__encoding__': _byte_encoding,
    }


NAIVE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
NAIVE_TIME_FORMAT = '%H:%M:%S.%fZ'
DATE_FORMAT = '%Y-%m-%d'


@coding.encode.register(types.MappingProxyType)
def _encode_mapping_proxy(obj):
    return dict(obj)  # Note: no special decoder; serialized as normal dict


@coding.encode.register(tuple)
def _encode_tuple(obj):
    return coding.marker(obj, list(obj))


@coding.register_decoder(tuple)
def _decode_tuple(data: List[Any]) -> tuple:
    return tuple(data)


@coding.encode.register(range)
def _encode_range(obj):
    data = {
        '__start__': obj.start,
        '__stop__': obj.stop,
        '__step__': obj.step,
    }
    return coding.marker(obj, data)


@coding.register_decoder(range)
def _decode_range(data: Dict[str, Any]) -> range:
    return range(data['__start__'], data['__stop__'], data['__step__'])


@coding.encode.register(set)
def _encode_set(obj):
    return coding.marker(obj, list(obj))


@coding.register_decoder(set)
def _decode_set(data: List[Any]) -> set:
    return set(data)


@coding.encode.register(frozenset)
def _encode_frozenset(obj):
    return coding.marker(obj, list(obj))


@coding.register_decoder(frozenset)
def _decode_frozenset(data: List[Any]) -> frozenset:
    return frozenset(data)


@coding.encode.register(complex)
def _encode_complex(obj):
    data = {'__real__': obj.real, '__imag__': obj.imag}
    return coding.marker(obj, data)


@coding.register_decoder(complex)
def _decode_complex(data: Dict[str, Any]) -> complex:
    return complex(data['__real__'], data['__imag__'])


@coding.encode.register(bytes)
def _encode_bytes(obj):
    return coding.marker(obj, _decode_byte_objects(obj))


@coding.register_decoder(bytes)
def _decode_bytes(data: Dict[str, Any]) -> bytes:
    return str.encode(data['__decoded__'], data['__encoding__'])


@coding.encode.register(bytearray)
def _encode_bytearray(obj):
    return coding.marker(obj, _decode_byte_objects(obj))


@coding.register_decoder(bytearray)
def _decode_bytearray(data: Dict[str, Any]) -> bytearray:
    return bytearray(data['__decoded__'], data['__encoding__'])


@coding.encode.register(decimal.Decimal)
def _encode_decimal(obj):
    return coding.marker(obj, str(obj))


@coding.register_decoder(decimal.Decimal)
def _decode_decimal(data: str) -> decimal.Decimal:
    return decimal.Decimal(data)


@coding.encode.register(fractions.Fraction)
def _encode_fraction(obj):
    return coding.marker(obj, str(obj))


@coding.register_decoder(fractions.Fraction)
def _decode_fraction(data: str) -> fractions.Fraction:
    return fractions.Fraction(data)


@coding.encode.register(dt.datetime)
def _encode_datetime(obj):
    # TODO: tz stuff, timespec stuff, sep
    try:
        data = obj.isoformat() + 'Z'
    except AttributeError:
        data = obj.strftime(NAIVE_DATETIME_FORMAT)
    return coding.marker(obj, data)


@coding.register_decoder(dt.datetime)
def _decode_datetime(data: str) -> dt.datetime:
    # TODO: isoformat() stuff + 'Z'
    return dt.datetime.strptime(data, NAIVE_DATETIME_FORMAT)


@coding.encode.register(dt.date)
def _encode_date(obj):
    try:
        data = obj.isoformat()
    except AttributeError:
        data = obj.strftime(DATE_FORMAT)
    return coding.marker(obj, data)


@coding.register_decoder(dt.date)
def _decode_date(data: str) -> dt.date:
    return dt.datetime.strptime(data, DATE_FORMAT).date()


@coding.encode.register(dt.time)
def _encode_time(obj):
    # TODO: tz stuff, timespec stuff
    try:
        data = obj.isoformat() + 'Z'
    except AttributeError:
        data = obj.strftime(NAIVE_TIME_FORMAT)
    return coding.marker(obj, data)


@coding.register_decoder(dt.time)
def _decode_time(data: str) -> dt.time:
    return dt.datetime.strptime(data, NAIVE_TIME_FORMAT).time()


@coding.encode.register(dt.timedelta)
def _encode_timedelta(obj):
    data = {
        '__days__': obj.days,
        '__seconds__': obj.seconds,
        '__microseconds__': obj.microseconds,
    }
    return coding.marker(obj, data)


@coding.register_decoder(dt.timedelta)
def _decode_timedelta(data: Dict[str, Any]) -> dt.timedelta:
    return dt.timedelta(
        days=data['days'],
        seconds=data['seconds'],
        microseconds=data['microseconds'],
    )
