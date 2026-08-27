"""Constants for the Events Calendar integration."""

DOMAIN = "events_calendar"

# Key: (UI Display Label, Internal Group ID, Default Enabled State)
EVENT_GROUPS = {
    "enable_lighting": ("Lighting", "lighting", True),
    "enable_holidays": ("Holidays", "holidays", False),
    "enable_birthdays": ("Birthdays", "birthdays", True),
    "enable_maintenance": ("Home Maintenance", "maintenance", False),
}
