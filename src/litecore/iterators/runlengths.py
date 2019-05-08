import dataclasses
import itertools
import logging

from typing import (
    Any,
    Iterator,
    Iterable,
)

log = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Run:
    """Component class for run-length encoding.

    Holds a value and the number of occurrences of that value for a segment of
    the run-legnth encoding.

    Attributes:
        value: the value
        times: the number of consecutive occurrences of that value

    """
    __slots__ = ('value', 'times')
    value: Any
    times: int

    @property
    def expansion(self) -> Iterator[Any]:
        """Return an iterator of the value repeated the number of times."""
        return itertools.repeat(self.value, self.times)


class RunLengths:
    """A simple run-legnth encoding.

    Represents an iterable as a sequence of Run objects, each containing a
    value and the number of consecutive occurrences of that value in that
    segment of the encoding.

    Arguments:
        iterable: the object to be run-length encoded

    >>> data = [1, 1, 1, 3, 3, 3, 3, 2, 2, 2]
    >>> runs = RunLengths(data)
    >>> list(runs.encoding)
    [Run(value=1, times=3), Run(value=3, times=4), Run(value=2, times=3)]
    >>> list(runs.expand)
    [1, 1, 1, 3, 3, 3, 3, 2, 2, 2]

    """
    __slots__ = ('_encoding')

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._encoding = [
            Run(value=value, times=len(list(run)))
            for value, run in itertools.groupby(iterable)
        ]

    @property
    def encoding(self) -> Iterator[Run]:
        """Iterator of the run-length encoding segmnents."""
        for run in self._encoding:
            yield run

    @property
    def expand(self) -> Iterator[Any]:
        """Iterator of the values of the original iterable."""
        return itertools.chain.from_iterable(
            run.expansion for run in self.encoding
        )
