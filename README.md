# Home Assistant Events Calendar

A custom Home Assistant calendar integration that dynamically generates calendar events from a simple `events.yaml` configuration file. 

Designed specifically for holiday lighting, seasonal automations, and recurring dates, it supports fixed dates, relative rule-based dates (e.g., 2nd Monday of October), Easter calculations, date range offsets, and event priorities for overlapping date ranges.

---

## Features

- 📅 **Dynamic Date Rule Engine:** Define fixed dates, relative floating dates, or Easter-relative dates easily in YAML.
- ⚖️ **Priority Conflict Resolution:** Resolves overlapping events (e.g., month-long Halloween themes vs. single-day Thanksgiving events) using customizable priority scoring.
- ⚡ **Lightweight & Efficient:** Evaluates dates natively in Python — eliminates the need for complex Jinja template sensors.
- 🎨 **WLED Automation Ready:** Works natively with standard Home Assistant calendar automations to select preset options dynamically.

---

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add `https://github.com/esand/ha-events-calendar` with category **Integration**.
4. Click **Add**, then find **Events Calendar** in HACS and click **Download**.
5. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the contents of `custom_components/events_calendar` from this repository.
2. Place the folder into your Home Assistant directory under `<config>/custom_components/events_calendar/`.
3. Restart Home Assistant.

---

## Configuration

Create a file named `events.yaml` in your main Home Assistant config folder (`/config/events.yaml`). An example [events.yaml](custom_components/events_calendar/events.yaml) is provided and loaded by default.

### Event Rule Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | String | Yes | — | Summary title shown on the calendar entity. |
| `type` | String | No | `fixed` | Rule type: `fixed`, `relative`, or `easter`. |
| `month` | Integer | Conditional | — | Month number (1-12). Required for `fixed` and `relative`. |
| `day` | Integer | Conditional | — | Day number (1-31). Required for `fixed`. |
| `weekday` | Integer | Conditional | — | Day of week for `relative` rules (0 = Monday, 6 = Sunday). |
| `week_number` | Integer | Conditional | — | Instance of weekday in month (1 = 1st, 2 = 2nd, -1 = last). |
| `priority` | Integer | No | `0` | Higher priority wins when multiple events overlap on the same date. |
| `offset_start_days` | Integer | No | `0` | Days to adjust event start date (negative starts earlier). |
| `offset_end_days` | Integer | No | `0` | Days to adjust event end date (positive extends later). |
| `span_weekend` | `boolean` | `false` | Automatically expands the start date to Saturday if the calculated start date falls on Sunday or Monday. |
| `observed` | `boolean` | `false` | Generates a secondary "Observed" event on the next available weekday if the event falls on a weekend. |

---

## Special Rules & Behavior

### Weekend Expansion (`span_weekend`)
When `span_weekend: true` is enabled:
* If the calculated event start date falls on a **Sunday**, the start date is pulled back 1 day to **Saturday**.
* If the calculated event start date falls on a **Monday**, the start date is pulled back 2 days to **Saturday**.
* If the start date falls on Tuesday through Saturday, no adjustment is made.
* *Note:* `span_weekend` only modifies the event **start date** (ensuring light automation starts for the entire weekend); it does not alter the event end date.

### Sequential Observed Holidays (`observed`)
When `observed: true` is set on a rule whose base date falls on a weekend (Saturday or Sunday), the integration generates an additional entry marked `(Observed)`:
* **Sequential Bump Guard:** If consecutive weekend holidays occur (such as Christmas Day on Saturday, Dec 25, and Boxing Day on Sunday, Dec 26), the second holiday automatically bumps to the next available weekday so two observed holidays never occupy the same day.
