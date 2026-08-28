"""Calendar platform for Events Calendar."""

from datetime import date, datetime, timedelta
import logging
import os

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.yaml import load_yaml

from .const import DOMAIN, EVENT_GROUPS
from .helpers import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up calendar entities based on enabled options."""
    yaml_path = self.hass.config.path("events.yaml")
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(os.path.dirname(__file__), "events.yaml")

    try:
        raw_events = await hass.async_add_executor_job(load_yaml, yaml_path)
    except Exception as err:
        _LOGGER.error("Failed to load events.yaml: %s", err)
        raw_events = {}

    entities = []
    options = entry.options or entry.data

    # Unpack 3 items per tuple: (group_title, group_type, default_enabled)
    for opt_key, (group_title, group_type, default_enabled) in EVENT_GROUPS.items():
        if options.get(opt_key, default_enabled):
            rules = raw_events.get(group_type, [])
            entities.append(
                GroupCalendarEntity(
                    group_title=group_title,
                    group_type=group_type,
                    entry_id=entry.entry_id,
                    rules=rules,
                )
            )

    async_add_entities(entities)


class GroupCalendarEntity(CalendarEntity):
    """Representation of a calendar entity for a specific event group."""

    def __init__(
        self,
        group_title: str,
        group_type: str,
        entry_id: str,
        rules: list[dict],
    ) -> None:
        """Initialize group calendar entity."""
        self._attr_name = group_title
        self._group_type = group_type
        self._attr_unique_id = f"{entry_id}_{group_type}"
        self._attr_translation_key = group_type  # Maps entity to icons.json
        self._rules = rules

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current active event or next upcoming event."""
        today = date.today()
        events = self._calculate_events_for_year(today.year)

        # 1. Currently active sorted by priority
        active_events = [e for e in events if e[1] <= today <= e[2]]

        if active_events:
            active_events.sort(key=lambda x: x[3], reverse=True)
            summary, start, end, _ = active_events[0]
            return CalendarEvent(summary=summary, start=start, end=end)

        # 2. Next upcoming in current year
        future_events = [e for e in events if e[1] > today]

        # 3. Next year check if none remaining
        if not future_events:
            future_events.extend(self._calculate_events_for_year(today.year + 1))

        if future_events:
            future_events.sort(key=lambda x: x[1])
            summary, start, end, _ = future_events[0]
            return CalendarEvent(summary=summary, start=start, end=end)

        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return all events overlapping the requested UI date range."""
        events_list = []

        for year in range(start_date.year, end_date.year + 1):
            for summary, event_start, event_end, _ in self._calculate_events_for_year(year):
                if event_start <= end_date.date() and event_end >= start_date.date():
                    events_list.append(
                        CalendarEvent(
                            summary=summary, start=event_start, end=event_end
                        )
                    )

        return events_list

    def _calculate_events_for_year(self, year: int) -> list[tuple[str, date, date, int]]:
        """Calculate event start and end dates based on loaded rules."""
        events = []

        for rule in self._rules:
            try:
                name = rule["name"]
                rule_type = rule.get("type", "fixed")
                start_offset = rule.get("offset_start_days", 0)
                end_offset = rule.get("offset_end_days", 0)
                priority = rule.get("priority", 0)

                base_date = None

                if rule_type == "easter":
                    base_date = get_easter_sunday(year)

                elif rule_type == "fixed":
                    base_date = date(year, rule["month"], rule["day"])

                elif rule_type == "relative":
                    base_date = get_relative_weekday(
                        year=year,
                        month=rule["month"],
                        target_weekday=rule["weekday"],
                        week_number=rule["week_number"],
                    )

                if base_date:
                    event_start = base_date + timedelta(days=start_offset)
                    event_end = base_date + timedelta(days=end_offset)
                    events.append((name, event_start, event_end, priority))

                    if rule.get("observed") and base_date.weekday() in (5, 6):
                        observed_date = get_observed_date(base_date)
                        if observed_date:
                            obs_start = observed_date + timedelta(days=start_offset)
                            obs_end = observed_date + timedelta(days=end_offset)
                            events.append((f"{name} (Observed)", obs_start, obs_end, priority))

            except Exception as err:
                _LOGGER.error(
                    "Error evaluating event rule '%s': %s", rule.get("name"), err
                )

        return events
