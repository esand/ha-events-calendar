"""Tests for Events Calendar config and options flows."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.events_calendar.const import DOMAIN


async def test_config_flow_user_step(hass: HomeAssistant):
    """Test initial setup flow via UI."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"instance_name": "My Custom Events"},
    )
    assert result2["type"] == "create_entry"
    assert result2["title"] == "My Custom Events"


async def test_options_flow(hass: HomeAssistant):
    """Test toggling calendar groups in options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Custom Events",
        options={"lighting": True, "holidays": False},
    )
    entry.add_to_hass(hass)

    mock_yaml = {
        "lighting": {"name": "Lighting Events", "events": []},
        "holidays": {"name": "Holidays", "events": []},
    }

    with patch(
        "custom_components.events_calendar.config_flow.async_load_events_yaml",
        return_value=mock_yaml,
    ):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] == "form"
        assert result["step_id"] == "init"

        # Update options: disable lighting, enable holidays
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"enabled_groups": ["holidays"]},
        )
        assert result2["type"] == "create_entry"
        assert entry.options == {"lighting": False, "holidays": True}
