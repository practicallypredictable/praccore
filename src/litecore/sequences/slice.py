from typing import (
    Any,
    Iterator,
    Optional,
    Sequence,
)


def adjust_slice_endpoint(
        *,
        length: int,
        endpoint: int,
        step: int = 1,
) -> int:
    if endpoint < 0:
        endpoint += length
        if endpoint < 0:
            endpoint = -1 if step < 0 else 0
    elif endpoint >= length:
        endpoint = length - 1 if step < 0 else length
    return endpoint


def adjust_slice_args(
        *,
        length: int,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
) -> int:
    if step is None:
        step = 1
    elif step == 0:
        raise ValueError('step cannot be 0')
    if start is None:
        start = length - 1 if step < 0 else 0
    else:
        start = adjust_slice_endpoint(
            length=length, endpoint=start, step=step)
    if stop is None:
        stop = -1 if step < 0 else length
    else:
        stop = adjust_slice_endpoint(
            length=length, endpoint=stop, step=step)
    return start, stop, step


def slice_indices(
        *,
        length: int,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
) -> Iterator[int]:
    start, stop, step = adjust_slice_args(
        length=length, start=start, stop=stop, step=step)
    index = start
    while (index > stop) if step < 0 else (index < stop):
        yield index
        index += step


def iter_slice(
        sequence: Sequence,
        *,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
) -> Iterator[Any]:
    for index in slice_indices(
            length=len(sequence), start=start, stop=stop, step=step):
        yield sequence[index]
