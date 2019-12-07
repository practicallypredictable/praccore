import datetime as dt
import functools

from typing import (
    Any,
    Callable,
    Optional,
)

import litecore.validation.base as base
import litecore.validation.specified as specified
import litecore.validation.exceptions as exc


def _reverse_strptime_args(format_string: str, date_string: str) -> dt.datetime:
    return dt.datetime.strptime(date_string, format_string)


def datetime_string_parser(format_string: str):
    return functools.partial(_reverse_strptime_args, format_string)


class DateAdapter:
    def __init__(self, func: Callable[[Any], dt.datetime]):
        self.datetime_maker = func

    def __call__(self, *args, **kwargs) -> dt.date:
        return self.datetime_maker(*args, **kwargs).date()


try:
    default_date_parser = dt.date.fromisoformat
    default_time_parser = None
    default_datetime_parser = dt.datetime.fromisoformat
except AttributeError:
    default_date_parser = DateAdapter(datetime_string_parser('%Y-%m-%d'))
    default_time_parser = None
    default_datetime_parser = None


def _validate_timezones(value: dt.datetime, validator):
    if validator.tz is not None and value.tzinfo is None:
        msg = 'value is timezone-naive, should be timezone-aware'
        raise exc.TimeZoneError(value, validator, None, None, msg)
    elif validator.tz is None and value.tzinfo is not None:
        msg = 'value is timezone-aware, should be timezone-naive'
        raise exc.TimeZoneError(value, validator, None, None, msg)


class Date(base.SimpleChoices):
    __slots__ = ('min_date', 'max_date', 'tz', 'parser') + base.get_slots(
        specified.SimpleChoices,
    )
    default_coerce_type = dt.date

    def __init__(
            self,
            *,
            min_date: Optional[dt.date] = None,
            max_date: Optional[dt.date] = None,
            tz: Optional[dt.timezone] = None,
            parser: Optional[Callable[[Any], dt.date]] = default_date_parser,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.min_date = min_date
        self.max_date = max_date
        self.tz = tz
        self.parser = parser

    def _validate(self, value: Any) -> Any:
        if isinstance(value, dt.datetime):
            _validate_timezones(value, self)
            if self.tz is not None and value.tzinfo is not None:
                value = value.astimezone(self.tz)
            value = value.date()
        if not isinstance(value, dt.date):
            if self.parser is not None:
                try:
                    value = self.parser(value)
                except Exception as err:
                    raise exc.ParseError(value, self, dt.date, err) from err
            else:
                raise exc.ValidationTypeError(value, self, dt.date)
        if self.min_date is not None and value < self.min_date:
            raise exc.BoundError(value, self, '>=', self.min_date)
        if self.max_date is not None and value > self.max_date:
            raise exc.BoundError(value, self, '<=', self.max_date)
        return super()._validate(value)

    @classmethod
    def relative(
            cls,
            *,
            min_delta: Optional[dt.timedelta] = None,
            max_delta: Optional[dt.timedelta] = None,
            **kwargs,
    ):
        today = dt.date.today()
        min_date = today + min_delta if min_delta is not None else None
        max_date = today + max_delta if max_delta is not None else None
        return cls(min_date=min_date, max_date=max_date, **kwargs)


class Time(base.SimpleChoices):
    __slots__ = ('min_time', 'max_time', 'tz', 'parser') + base.get_slots(
        specified.SimpleChoices,
    )
    default_coerce_type = dt.time

    def __init__(
            self,
            *,
            min_time: Optional[dt.time] = None,
            max_time: Optional[dt.time] = None,
            tz: Optional[dt.timezone] = None,
            parser: Optional[Callable[[Any], dt.time]] = default_time_parser,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.min_time = min_time
        self.max_time = max_time
        self.tz = tz
        self.parser = parser

    def _validate(self, value: Any) -> Any:
        if isinstance(value, dt.datetime):
            if self.tz is not None and value.tzinfo is not None:
                value = value.astimezone(self.tz)
            value = value.time()
        if not isinstance(value, dt.time):
            if self.parser is not None:
                try:
                    value = self.parser(value)
                except Exception as err:
                    raise exc.ParseError(value, self, dt.time, err) from err
            else:
                raise exc.ValidationTypeError(value, self, dt.time)
        if self.min_time is not None and value < self.min_time:
            raise exc.BoundError(value, self, '>=', self.min_date)
        if self.max_time is not None and value > self.max_time:
            raise exc.BoundError(value, self, '<=', self.max_time)
        return super()._validate(value)

    @classmethod
    def relative(
            cls,
            *,
            min_delta: Optional[dt.timedelta] = None,
            max_delta: Optional[dt.timedelta] = None,
            tz: Optional[dt.timezone] = None,
            **kwargs,
    ):
        if tz is not None:
            now = dt.datetime.now().astimezone().timetz()
        else:
            now = dt.datetime.now().time()
        min_time = now + min_delta if min_delta is not None else None
        max_time = now + max_delta if max_delta is not None else None
        return cls(
            min_time=min_time,
            max_time=max_time,
            tz=tz,
            **kwargs,
        )


class DateTime(base.SimpleChoices):
    __slots__ = ('min_datetime', 'max_datetime', 'tz', 'parser') + base.get_slots(
        specified.SimpleChoices,
    )
    default_coerce_type = dt.datetime

    def __init__(
            self,
            *,
            min_datetime: Optional[dt.datetime] = None,
            max_datetime: Optional[dt.datetime] = None,
            tz: Optional[dt.timezone] = None,
            parser: Optional[Callable[[Any], dt.datetime]] = default_datetime_parser,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if tz is not None:
            if self.min_datetime is not None and self.min_datetime.tzinfo is None:
                msg = f'min datetime should be timezone-aware'
                raise ValueError(msg)
            if self.max_datetime is not None and self.max_datetime.tzinfo is None:
                msg = f'max datetime should be timezone-aware'
                raise ValueError(msg)
        else:
            if self.min_datetime or self.min_datetime.tzinfo:
                msg = f'min datetime should be timezone-naive'
                raise ValueError(msg)
            if self.max_datetime or self.max_datetime.tzinfo:
                msg = f'max datetime should be timezone-naive'
                raise ValueError(msg)
        self.min_datetime = min_datetime
        self.max_datetime = max_datetime
        self.tz = tz
        self.parser = parser

    def _validate(self, value: Any) -> Any:
        if isinstance(value, dt.date):
            value = dt.datetime.combine(value, dt.time(tzinfo=self.tz))
        if not isinstance(value, dt.datetime):
            if self.parser is not None:
                try:
                    value = self.parser(value)
                except Exception as err:
                    raise exc.ParseError(value, self, dt.datetime, err) from err
            else:
                raise exc.ValidationTypeError(value, self, dt.datetime)
        _validate_timezones(value, self)
        if self.min_datetime is not None and value < self.min_datetime:
            raise exc.BoundError(value, self, '>=', self.min_datetime)
        if self.max_datetime is not None and value > self.max_datetime:
            raise exc.BoundError(value, self, '<=', self.max_datetime)
        return super()._validate(value)

    @classmethod
    def relative(
            cls,
            *,
            min_delta: Optional[dt.timedelta] = None,
            max_delta: Optional[dt.timedelta] = None,
            tz: Optional[dt.timezone] = None,
            **kwargs,
    ):
        if tz is not None:
            now = dt.datetime.now().astimezone()
        else:
            now = dt.datetime.now()
        min_datetime = now + min_delta if min_delta is not None else None
        max_datetime = now + max_delta if max_delta is not None else None
        return cls(min_datetime=min_datetime, max_datetime=max_datetime, **kwargs)
