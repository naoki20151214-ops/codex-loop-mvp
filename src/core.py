from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9), name="JST")


def format_jst(dt: datetime) -> str:
    """Format a datetime in Japan Standard Time.

    Naive datetimes are treated as UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S JST")
