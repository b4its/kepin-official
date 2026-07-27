from __future__ import annotations
from datetime import date, timedelta, timezone, datetime
from typing import Literal

Preset = Literal["last_week", "last_2_weeks", "last_3_weeks", "last_month"]


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def resolve_period(
    preset: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[date, date]:
    """Return (start, end) dates inclusive."""
    today = today_utc()
    if preset:
        days = {"last_week": 7, "last_2_weeks": 14, "last_3_weeks": 21, "last_month": 30}.get(preset, 7)
        return today - timedelta(days=days - 1), today
    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("startDate must be <= endDate")
        return start_date, end_date
    return today - timedelta(days=6), today
