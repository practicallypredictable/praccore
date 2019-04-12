import logging

from typing import (
    Any,
    Callable,
    Container,
    Tuple,
)

log = logging.getLogger(__name__)


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
