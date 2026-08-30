"""Helper functions and custom date algorithms for Events Calendar."""

import calendar as py_calendar
from datetime import date, timedelta


def get_easter_sunday(year: int) -> date:
    """Calculate Easter Sunday for a given year."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    return date(year, month, day)

def get_relative_weekday(year: int, month: int, target_weekday: int, week_number: int) -> date:
    """Find the Nth target weekday of a month.

    target_weekday: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    week_number: 1-based index (e.g., 4 for 4th occurrence, -1 for last occurrence)
    """
    cal = py_calendar.monthcalendar(year, month)
    matches = [week[target_weekday] for week in cal if week[target_weekday] != 0]

    if week_number < 0:
        day = matches[week_number]
    else:
        day = matches[week_number - 1]

    return date(year, month, day)

def get_observed_date(
    base_date: date, existing_observed: set[date] | None = None
) -> date | None:
    """Calculate observed date for a weekend holiday, bumping past already occupied dates."""
    if base_date.weekday() not in (5, 6):
        return None

    if existing_observed is None:
        existing_observed = set()

    if base_date.weekday() == 5:
        target_date = base_date + timedelta(days=2)
    else:
        target_date = base_date + timedelta(days=1)

    # Bump forward to next weekday if target_date is already an observed date
    while target_date in existing_observed or target_date.weekday() in (5, 6):
        target_date += timedelta(days=1)

    existing_observed.add(target_date)
    return target_date

def expand_event_to_weekend(start_date: date) -> date:
    """Expand event to cover the full weekend if it starts on Sunday, or Monday."""
    if start_date.weekday() == 6:
        return start_date - timedelta(days=1)
    elif start_date.weekday() == 0:
        return start_date - timedelta(days=2)

    return start_date
