import operator

from typing import (
    Any,
    Iterator,
    Optional,
    Sequence,
    Union,
)


def stop_index(index_or_slice: Union[int, slice]) -> Union[None, int]:
    try:
        stop = index_or_slice.stop
        if stop is None:
            return None
        step = index_or_slice.step
        if step is None:
            step = 1
        elif step == 0:
            raise ValueError(f'slice step cannot be zero')
        start = index_or_slice.start
        if start is None:
            start = 0 if step > 0 else -1
        return range(start, stop, step)[-1]
    except AttributeError:
        try:
            return operator.index(index_or_slice)
        except TypeError as err:
            msg = f'expected an integer or a slice; got {index_or_slice!r}'
            raise TypeError(msg) from err


def adjust_endpoint(
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


def adjust_args(
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
        start = adjust_endpoint(
            length=length, endpoint=start, step=step)
    if stop is None:
        stop = -1 if step < 0 else length
    else:
        stop = adjust_endpoint(
            length=length, endpoint=stop, step=step)
    return start, stop, step


def slice_indices(
        *,
        length: int,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
) -> Iterator[int]:
    start, stop, step = adjust_args(
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
