import typing

import litecore.getters


def pluck(
        iterable: typing.Iterable[typing.Any],
        *,
        fields: typing.Sequence[str],
        getter_factory: typing.Callable = litecore.getters.fieldgetter,
        **kwargs,
) -> typing.Iterator[typing.Any]:
    """

    Examples:

    >>> import datetime as dt
    >>> dates = [
    ...     dt.datetime(2019, 5, 17, 8, 45),
    ...     dt.datetime(2019, 5, 18, 12, 15),
    ...     dt.datetime(2019, 5, 19, 19, 45),
    ... ]
    >>> employees = [
    ...     {'id': 1, 'name': 'Alice', 'title': 'CEO'},
    ...     {'id': 2, 'name': 'Bob', 'title': 'CFO', 'to_be_fired': True},
    ...     {'id': 3, 'name': 'Charlie', 'title': 'CMO'},
    ...     {'id': 4, 'name': 'Dierdre', 'title': 'COO', 'to_be_fired': True},
    ...     {'id': 5, 'name': 'Edward', 'title': 'CTO'},
    ... ]
    >>> list(pluck(dates, fields=('day',)))
    [17, 18, 19]
    >>> list(pluck(dates, fields=('day', 'month',)))
    [(17, 5), (18, 5), (19, 5)]
    >>> list(pluck(dates, fields=('day', 'wrong',)))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    litecore.getters.GetFieldError: data ... does not have all fields ('day', 'wrong') ...
    >>> list(pluck(dates, fields=(2,)))
    Traceback (most recent call last):
     ...
    TypeError: attribute name must be a string
    >>> list(pluck(
    ...     employees,
    ...     fields=('name', 'to_be_fired',),
    ...     default=False,
    ... ))
    [('Alice', False), ('Bob', True), ('Charlie', False), ('Dierdre', True), ('Edward', False)]

    """
    getter = getter_factory(*fields, **kwargs)
    for item in iterable:
        yield getter(item)
