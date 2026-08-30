"""Tests for Events Calendar YAML loader."""

from unittest.mock import mock_open, patch

from homeassistant.core import HomeAssistant

from custom_components.events_calendar.loader import async_load_events_yaml


async def test_async_load_events_yaml_success(hass: HomeAssistant):
    """Test successfully reading and parsing valid YAML data."""
    mock_yaml_data = (
        "lighting:\n"
        "  name: 'Lighting Events'\n"
        "  icon: 'mdi:lamp'\n"
        "  events: []\n"
    )

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_yaml_data)):
        data = await async_load_events_yaml(hass)
        assert "lighting" in data
        assert data["lighting"]["name"] == "Lighting Events"


async def test_async_load_events_yaml_error_handling(hass: HomeAssistant):
    """Test fallback when YAML file read raises an exception."""
    with patch("os.path.exists", return_value=True), \
         patch("homeassistant.util.yaml.load_yaml", side_effect=OSError("File unreadable")):
        data = await async_load_events_yaml(hass)
        assert data == {}
