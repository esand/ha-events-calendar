"""Config and Options flow for Events Calendar."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN
from .loader import async_load_events_yaml

_LOGGER = logging.getLogger(__name__)


class EventCalendarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial creation step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["instance_name"],
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("instance_name", default="Events Calendar"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return EventsCalendarOptionsFlowHandler()


class EventsCalendarOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle configuration options (toggling calendars)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage calendar on/off toggles."""
        raw_data = await async_load_events_yaml(self.hass)

        if user_input is not None:
            selected_groups = set(user_input.get("enabled_groups", []))
            new_options = {
                group_key: (group_key in selected_groups)
                for group_key in raw_data
                if isinstance(raw_data[group_key], dict)
            }
            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options

        options_list = [
            SelectOptionDict(
                value=group_key,
                label=group_config.get("name", group_key.replace("_", " ").title()),
            )
            for group_key, group_config in raw_data.items()
            if isinstance(group_config, dict)
        ]

        currently_enabled = [
            group_key
            for group_key, group_config in raw_data.items()
            if isinstance(group_config, dict)
            and options.get(group_key, True)
        ]

        schema_dict = {
            vol.Optional(
                "enabled_groups",
                default=currently_enabled,
            ): SelectSelector(
                SelectSelectorConfig(
                    options=options_list,
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            )
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )