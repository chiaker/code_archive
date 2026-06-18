"""Date and time helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    """Return the current timezone-aware UTC time."""

    return datetime.now(timezone.utc)


def in_days(days: int) -> datetime:
    """Return a UTC datetime offset from now by a number of days."""

    return utcnow() + timedelta(days=days)


def isoformat(value: datetime) -> str:
    """Format a datetime as an ISO-8601 string."""

    return value.isoformat()
