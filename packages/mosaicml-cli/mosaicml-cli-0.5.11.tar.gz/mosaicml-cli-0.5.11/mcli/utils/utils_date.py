"""This Module stores utils for pretty printing Datetime objects"""
import datetime
from enum import Enum

from dateutil import tz


def get_human_readable_date(
        dt: datetime.datetime,
        *,
        to_tz=tz.tzlocal(),
) -> str:
    """Parses a datetime string into friendly readable form

        Args:
            dt: Datetime string to parse
            to_tz: Timezone to return the string in
                By default, return in the local timezone

        Returns:
            Formatted datetime string in specified timezone
    """
    if not dt.tzinfo:
        from_tz = tz.UTC
        dt = dt.replace(tzinfo=from_tz)

    dt_in_tz = dt.astimezone(to_tz)

    dt_formatted: str = f'{dt_in_tz:%Y-%m-%d %I:%M%p}'
    return dt_formatted


class TimestampPrecision(Enum):
    """Enum for timestamp precision"""
    DAY = 'day'
    MINUTE = 'minute'
    SECOND = 'second'


def format_timestamp(timestamp: datetime.datetime, precision: TimestampPrecision = TimestampPrecision.MINUTE) -> str:
    """Format timestamps into a human-readable string in the local timezone.
    The precision can be controlled by the `precision` argument.

    TODO(jerry/MCLOUD-3046): Replace both get_human_readable_date() and mcl.cli.m_get.display with this function.

    Args:
        timestamp: The timestamp to format
        precision: The precision to use when formatting the timestamp. Defaults to `TimestampPrecision.MINUTE`.

    Returns:
        The formatted timestamp string.

    Raises:
        ValueError: If the the timestamp is invalid or outside of the datetime supported range.
    """
    if precision == TimestampPrecision.DAY:
        dt_format = '%Y-%m-%d'
    elif precision == TimestampPrecision.MINUTE:
        dt_format = '%Y-%m-%d %I:%M %p'
    elif precision == TimestampPrecision.SECOND:
        dt_format = '%Y-%m-%d %I:%M:%S %p'

    timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo  # Get the local timezone
    return timestamp.astimezone(timezone).strftime(dt_format)
