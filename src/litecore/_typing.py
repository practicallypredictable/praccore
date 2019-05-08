from typing import (
    Hashable,
    TypeVar,
)

T = TypeVar('T')  # generic type
KT = TypeVar('KT', str, Hashable)  # key type
VT = TypeVar('VT')  # value type
HVT = TypeVar('HVT')  # hashable value type
