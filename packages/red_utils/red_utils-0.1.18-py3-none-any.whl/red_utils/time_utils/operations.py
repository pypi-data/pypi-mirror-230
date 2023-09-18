from __future__ import annotations

import datetime

from datetime import (
    datetime as dt,
    timedelta,
)
from typing import Union

from .constants import default_format, twelve_hour_format

import arrow

def datetime_as_str(ts: dt = None, format: str = default_format) -> str:
    """Convert a datetime.datetime object to a string.

    datetime.datetime() -> str()
    """
    _ts: str = ts.strftime(format=format)

    return _ts


def datetime_as_dt(ts: str = None, format: str = default_format) -> dt:
    """Convert a datetime string to a datetime.datetime object.

    str() -> datetime.datetime()
    """
    _ts: dt = dt.strptime(ts, format)

    return _ts


def get_ts(as_str: bool = False, format: str = default_format) -> Union[dt, str]:
    """Get a timestamp object.

    Returns a datetime.datetime by default. If as_str is True, converts datetime to
    a string and returns.
    """
    now: dt = dt.now()

    if as_str:
        now: str = datetime_as_str(ts=now, format=format)

    return now


def shift_ts(
    start_date: Union[datetime.datetime, str, arrow.Arrow] = None,
    _tz: str = "US/Eastern",
    target_tz: str = "US/Eastern",
    period: str = None,
    amount: int = 0,
) -> arrow.Arrow:
    """Shift a timestamp forward/back a period of time (years, months, weeks, days, hours, minutes, seconds).

    Arguments:
    ---------
        start_date (datetime.datetime, str, arrow.Arrow):
            The timestamp you already have that you want to shift/convert.
            If start_date is not of type (arrow.Arrow), the function will try to convert it
        _tz:
            The timezone for the starting timestamp.
        target_tz:
            The timezone for the shifted timestamp. If no target_tz is passed, it will default
            to the same value as _tz.
        period:
            The period of time to shift the timestamp forward/backward. Must be one of:
            [years, months, weeks, days, hours, minutes, seconds]
        amount:
            A positive or negative integer value (i.e. +1/-1) to shift the timestamp. Positive integer
            values can be passed explicitly or implicitly, i.e. amount=1 OR amount=+1.

    Example:
    -------
        _tz = "US/Eastern"
        target_tz = "UTC"
        _start_date_time_str = "2022-08-12 00:00:00"
        start_date = arrow.get(_start_date_time_str, tzinfo=_tz)

        ## start_date = 2022-08-19T00:00:00-04:00
    """
    ## List of accepted values for 'period'
    valid_time_periods: list[str] = [
        "years",
        "months",
        "weeks",
        "days",
        "hours",
        "minutes",
        "seconds",
    ]
    ## Validate inputs
    if not period:
        raise ValueError(
            f"Missing a period of time. Must be one of {valid_time_periods}"
        )
    if not isinstance(period, str) and not isinstance(period, datetime.datetime):
        raise TypeError(
            f"Invalid type for period: ({type(period)}). Must be one of [str, datetime.datetime]"
        )
    if period not in valid_time_periods:
        raise TypeError(
            f"Invalid period of time: [{period}]. Must be one of {valid_time_periods}"
        )
    if not amount:
        raise ValueError("Missing amount of time to shift timestamp")
    ## Validate timezones
    if not _tz:
        raise ValueError("Missing starting timezone")
    if not target_tz:
        try:
            ## Set target_tz to same timezone as _tz if no value was passed
            target_tz = _tz
        except Exception as exc:
            raise Exception(f"Unhandled exception setting target_tz. Details: {exc}")
    if not start_date:
        raise ValueError("Missing a start date")
    if not isinstance(start_date, arrow.Arrow):
        start_date = arrow.get(start_date, tzinfo=_tz)

    try:
        ## Initialize return timestamp
        return_ts: arrow.Arrow = None

        match period:
            case "years":
                return_ts: arrow.Arrow = start_date.shift(years=amount)
            case "months":
                return_ts: arrow.Arrow = start_date.shift(months=amount)
            case "weeks":
                return_ts: arrow.Arrow = start_date.shift(weeks=amount)
            case "days":
                return_ts: arrow.Arrow = start_date.shift(days=amount)
            case "hours":
                return_ts: arrow.Arrow = start_date.shift(hours=amount)
            case "minutes":
                return_ts: arrow.Arrow = start_date.shift(minutes=amount)
            case "seconds":
                return_ts: arrow.Arrow = start_date.shift(seconds=amount)
            case _:
                raise NotImplementedError(
                    f"Support for shift type: {period} not yet implemented."
                )

        return return_ts
    except Exception as exc:
        raise Exception(f"Unhandled exception")


if __name__ == "__main__":
    ts = get_ts()

    print(f"Timestamp ({type(ts)}): {ts}")

    as_str: str = get_ts(as_str=True)
    print(f"Timestamp: datetime to str Type({type(as_str).__name__}): {as_str}")

    as_dt: dt = datetime_as_dt(ts=as_str)
    print(f"Timestamp: str to datetime Type({type(as_dt).__name__}): {as_dt}")
