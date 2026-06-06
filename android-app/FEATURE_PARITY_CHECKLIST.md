# Feature Parity Checklist (Python v16 -> Android)

Source analyzed: `references/Schedule_Upgrade_with_name_fixed_16.py`

## Screens / Views
- [x] Main planner screen with title and user name (`<name> • 4-On / 4-Off Planner`)
- [x] Four day tabs (Day 1..Day 4) with per-day title and activities
- [x] Cycle summary view for next 8 days from off-cycle start date
- [x] Personal notes area
- [x] Yearly calendar view with cycle-based day coloring and year navigation

## Buttons / Actions
- [x] Set name (first + last)
- [x] Toggle light/dark theme
- [x] Save local schedule state
- [x] Load local schedule state
- [x] Export JSON file
- [x] Import JSON file
- [x] Yearly calendar open
- [x] Category filter chips + Clear filter
- [x] Edit activity (time, description, category)

## Data Fields
- [x] Off-cycle start date
- [x] User full name
- [x] Notes text
- [x] Schedule days keyed by id (`"1".."4"`)
- [x] Day title
- [x] Activity rows: `[time, description, category]`
- [x] Categories: `sleep, morning, afternoon, evening, medicine, gym, coding, meal`

## Storage Format
- [x] Python-compatible JSON shape:
  - `schedule: { "1": { title, activities: [[time, activity, category], ...] }, ... }`
  - `notes: string`
  - `startDate: "MM/DD/YYYY"`
  - `userName: string`
  - `workMode: string` (Android extension; safely optional for Python compatibility)
- [x] Local persistence via Android DataStore
- [x] Import/export via system document picker

## Core Logic
- [x] 8-day cycle calculation from selected off-cycle start date
  - offsets `0..3` => `Off day 1..4`
  - offsets `4..7` => `On day 1..4`
- [x] Yearly calendar coloring based on modulo-8 position
  - `0..3` off-cycle color
  - `4..5` on-cycle day color
  - `6..7` on-cycle night color
- [x] Input validation for activity edit (required time + activity + category)
- [x] Category filtering per selected day tab
