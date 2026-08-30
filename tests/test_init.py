"""Tests for Events Calendar __init__ setup, unload, and update listener."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.events_calendar.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_unload_and_update_listener(hass: HomeAssistant) -> None:
    """Test setting up, reloading via options update, and unloading a config entry."""
    mock_yaml = {
        "holidays": {
            "name": "Holidays",
            "events": [],
        }
    }

    entry = MockConfigEntry(domain=DOMAIN, data={}, options={"holidays": True})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.events_calendar.calendar.async_load_events_yaml",
        return_value=mock_yaml,
    ):
        # Setup entry via Home Assistant framework
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED

        # Update options to fire update_listener (Covers __init__.py Line 25)
        hass.config_entries.async_update_entry(
            entry, options={"holidays": False}
        )
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED

        # Unload entry
        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.NOT_LOADED
