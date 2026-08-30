"""Tests for Events Calendar helpers."""

from datetime import date

from custom_components.events_calendar.helpers import *


def test_get_easter_sunday():
    """Test Easter Sunday calculation for known years."""
    assert get_easter_sunday(2024) == date(2024, 3, 31)
    assert get_easter_sunday(2025) == date(2025, 4, 20)
    assert get_easter_sunday(2028) == date(2028, 4, 16)


def test_get_relative_weekday():
    """Test nth weekday calculations."""
    # 3rd Monday in February 2028 (Family Day / Presidents Day)
    assert get_relative_weekday(2028, 2, 0, 3) == date(2028, 2, 21)

    # Last Monday in May 2028 (Memorial Day, week_number = -1)
    assert get_relative_weekday(2028, 5, 0, -1) == date(2028, 5, 29)


def test_get_relative_weekday_negative_index() -> None:
    """Test get_relative_weekday with a negative week_number (e.g., last occurrence)."""
    # Last Monday of May 2026 (May 25, 2026)
    last_monday = get_relative_weekday(year=2026, month=5, target_weekday=0, week_number=-1)
    assert last_monday == date(2026, 5, 25)


def test_expand_event_to_weekend():
    """Test weekend expansion for start dates."""
    # Sunday start -> rolls back 1 day to Saturday
    sunday_start = date(2028, 2, 13)
    assert expand_event_to_weekend(sunday_start) == date(2028, 2, 12)

    # Monday start -> rolls back 2 days to Saturday (e.g. Valentine's 2028)
    monday_start = date(2028, 2, 14)
    assert expand_event_to_weekend(monday_start) == date(2028, 2, 12)

    # Saturday start -> remains Saturday
    saturday_start = date(2028, 2, 12)
    assert expand_event_to_weekend(saturday_start) == date(2028, 2, 12)

    # Mid-week start -> no change
    wednesday_start = date(2028, 2, 16)
    assert expand_event_to_weekend(wednesday_start) == date(2028, 2, 16)


def test_get_observed_date_default_existing_observed() -> None:
    """Test get_observed_date initializes existing_observed set when None is passed (Line 50)."""
    # Saturday, July 4, 2026 (base_date on Saturday triggers observed date calculation)
    saturday_date = date(2026, 7, 4)

    # Calling without passing second argument hits `if existing_observed is None: existing_observed = set()`
    observed = get_observed_date(saturday_date)
    
    # Saturday observed date shifts to Monday, July 6
    assert observed == date(2026, 7, 6)


def test_get_observed_date_and_sequential_bumping():
    """Test weekend holiday observation and sequential bumping for conflicts."""
    used_observed: set[date] = set()

    # Christmas Day 2027 (Saturday, Dec 25) -> Observed Mon, Dec 27
    christmas = date(2027, 12, 25)
    obs1 = get_observed_date(christmas, used_observed)
    assert obs1 == date(2027, 12, 27)

    # Boxing Day 2027 (Sunday, Dec 26) -> Bumps to Tue, Dec 28 because Dec 27 is taken
    boxing = date(2027, 12, 26)
    obs2 = get_observed_date(boxing, used_observed)
    assert obs2 == date(2027, 12, 28)

    # Weekday event -> Returns None
    weekday = date(2027, 12, 24)
    assert get_observed_date(weekday, used_observed) is None
