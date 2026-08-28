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

Create a file named `events.yaml` in your main Home Assistant config folder (`/config/events.yaml`). An example [events.yaml](events.yaml) is provided as well as a shorter example below.

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

---

### Example `events.yaml`

```yaml
lighting:
  # Fixed Date (Single Day)
  - name: "Canada Day"
    type: "fixed"
    month: 7
    day: 1

  # Month-Long Event (Low Priority)
  - name: "Halloween"
    type: "fixed"
    month: 10
    day: 31
    priority: 1
    offset_start_days: -30
    offset_end_days: 0

  # Relative Date: 2nd Monday of October (Thanksgiving in Canada)
  # High Priority overrides Halloween on overlapping days
  - name: "Thanksgiving"
    type: "relative"
    month: 10
    weekday: 0         # Monday
    week_number: 2     # 2nd Monday
    priority: 10
    offset_start_days: -1
    offset_end_days: 0

  # Easter Relative Event
  - name: "Easter"
    type: "easter"
    offset_start_days: -2  # Starts Good Friday
    offset_end_days: 1     # Ends Easter Monday
