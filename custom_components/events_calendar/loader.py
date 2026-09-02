"""YAML loader for Events Calendar."""

from __future__ import annotations

import logging
import os
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import load_yaml

_LOGGER = logging.getLogger(__name__)


async def async_load_events_yaml(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Load and parse the events.yaml configuration file."""
    yaml_path = hass.config.path("events.yaml")
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(os.path.dirname(__file__), "events.yaml")

    try:
        loaded = await hass.async_add_executor_job(load_yaml, yaml_path)
        if isinstance(loaded, dict):
            return {
                k: v for k, v in loaded.items() if isinstance(v, dict)
            }
    except (HomeAssistantError, OSError) as err:
        _LOGGER.error("Failed to load events.yaml: %s", err)

    return {}
