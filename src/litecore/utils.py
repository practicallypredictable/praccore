__all__ = (
    'to_str',
    'to_bytes',
)

from typing import (
    Any,
    Callable,
    Container,
    Optional,
    Tuple,
    Union,
)

_DEFAULT_ENCODING = 'utf-8'


def to_str(
        str_or_bytes: Union[str, bytes],
        *,
        decode_from: str = _DEFAULT_ENCODING,
) -> str:
    if isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(decode_from)
    else:
        return str_or_bytes


def to_bytes(
        str_or_bytes: Union[str, bytes],
        *,
        encode_to: str = _DEFAULT_ENCODING,
) -> bytes:
    if isinstance(str_or_bytes, str):
        return str_or_bytes.encode(encode_to)
    else:
        return str_or_bytes


def constant_factory(constant: Any) -> Callable[[], Any]:
    return lambda: constant


def call_counter(*, default: Optional[Any] = None):
    class _MissingCounter:
        def __init__(self, *, default: Optional[Any] = None) -> None:
            self.times_called = 0
            self.default = default
    

def prioritize(
        group: Container) -> Callable[[Any], Tuple[int, Any]]:
    def modifier(value: Any) -> Tuple[int, Any]:
        return (0, value) if value in group else (1, value)
    return modifier


def prioritize_where(
        condition: Callable[[Any], bool]) -> Callable[[Any], Tuple[int, Any]]:
    def modifier(value: Any) -> Tuple[int, Any]:
        return (0, value) if condition(value) else (1, value)
    return modifier
