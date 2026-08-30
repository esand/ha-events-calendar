"""Tests for Events Calendar entity platform."""

from datetime import date
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import parse_datetime
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.events_calendar.calendar import GroupCalendarEntity
from custom_components.events_calendar.const import DOMAIN


async def test_calendar_setup_and_events(
    hass: HomeAssistant, freezer
) -> None:
    """Test setup of calendar entities and calculation of events."""
    freezer.move_to("2028-02-01T00:00:00Z")

    mock_yaml = {
        "lighting": {
            "name": "Lighting Events",
            "icon": "mdi:outdoor-lamp",
            "events": [
                {
                    "name": "Valentine's Day",
                    "type": "fixed",
                    "month": 2,
                    "day": 14,
                    "span_weekend": True,
                }
            ],
        }
    }

    entry = MockConfigEntry(domain=DOMAIN, title="Custom Events", options={})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.events_calendar.calendar.async_load_events_yaml",
        return_value=mock_yaml,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Verify calendar entity was created
    state = hass.states.get("calendar.lighting_events")
    assert state is not None
    assert state.attributes["friendly_name"] == "Lighting Events"
    assert state.attributes["icon"] == "mdi:outdoor-lamp"

    # Query calendar events for Feb 2028
    start_date = parse_datetime("2028-02-01T00:00:00Z")
    end_date = parse_datetime("2028-02-28T23:59:59Z")

    entity = hass.data["calendar"].get_entity("calendar.lighting_events")
    events = await entity.async_get_events(hass, start_date, end_date)

    assert len(events) == 1
    assert events[0].start == date(2028, 2, 12)
    assert events[0].end == date(2028, 2, 14)
    assert events[0].summary == "Valentine's Day"


@pytest.mark.asyncio
async def test_async_setup_entry_edge_cases(hass: HomeAssistant) -> None:
    """Test setup skipping non-dict groups and disabled groups in options."""
    mock_raw_data = {
        "invalid_group": "not_a_dict",
        "disabled_group": {
            "name": "Disabled",
            "events": [],
        },
        "enabled_group": {"name": "Enabled", "events": []},
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        options={"disabled_group": False, "enabled_group": True},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.events_calendar.calendar.async_load_events_yaml",
        return_value=mock_raw_data,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    enabled_state = hass.states.get("calendar.enabled")
    assert enabled_state is not None
    assert enabled_state.attributes["friendly_name"] == "Enabled"
    assert hass.states.get("calendar.disabled_group") is None


async def test_calendar_entity_empty_rules_event_property() -> None:
    """Test event property when no rules exist returns None."""
    entity = GroupCalendarEntity(
        group_key="empty",
        group_name="Empty Calendar",
        icon="mdi:calendar",
        entry_id="123",
        rules=[],
    )

    assert entity.event is None


async def test_calendar_entity_active_event(freezer) -> None:
    """Test event property when an event is currently active."""
    freezer.move_to("2026-12-25T12:00:00Z")

    rules = [
        {
            "name": "Christmas",
            "type": "fixed",
            "month": 12,
            "day": 25,
        }
    ]

    entity = GroupCalendarEntity(
        group_key="holidays",
        group_name="Holidays",
        icon="mdi:calendar",
        entry_id="123",
        rules=rules,
    )

    active_event = entity.event
    assert active_event is not None
    assert active_event.summary == "Christmas"


async def test_calendar_entity_future_event_lines_77_79(freezer) -> None:
    """Explicitly test future event branch (Lines 77-79)."""
    freezer.move_to("2026-01-01T00:00:00Z")

    rules = [
        {
            "name": "Independence Day",
            "type": "fixed",
            "month": 7,
            "day": 4,
        }
    ]

    entity = GroupCalendarEntity(
        group_key="holidays",
        group_name="Holidays",
        icon="mdi:calendar",
        entry_id="123",
        rules=rules,
    )

    next_event = entity.event
    assert next_event is not None
    assert next_event.summary == "Independence Day"
    assert next_event.start == date(2026, 7, 4)


async def test_calculate_events_malformed_rule_exception() -> None:
    """Test rule parsing error handling when a rule raises an exception."""
    invalid_rules = [
        {"name": "Bad Fixed Rule", "type": "fixed"}
    ]

    entity = GroupCalendarEntity(
        group_key="test",
        group_name="Test",
        icon="mdi:calendar",
        entry_id="123",
        rules=invalid_rules,
    )

    with patch("custom_components.events_calendar.calendar._LOGGER.error") as mock_log_error:
        events = entity._calculate_events_for_year(2026)
        assert events == []
        mock_log_error.assert_called_once()
        assert mock_log_error.call_args[0][1] == "Bad Fixed Rule"
