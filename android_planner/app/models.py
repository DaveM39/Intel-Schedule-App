from dataclasses import dataclass
from typing import List, Dict

# Category colour mapping used throughout the app
CATEGORY_COLORS: Dict[str, str] = {
    "sleep": "#D0E8FF",
    "morning": "#CFF5E7",
    "afternoon": "#FFE5B4",
    "evening": "#FFC1C1",
    "medicine": "#F7B5B8",
    "gym": "#E0D4FD",
    "coding": "#C7E6FF",
    "meal": "#FFF8B8",
}

ON_CYCLE_COLOR_LIGHT = "#FFD3D3"
OFF_CYCLE_COLOR_LIGHT = "#D3FFD3"

@dataclass
class Activity:
    """Single schedule entry."""
    time: str
    description: str
    category: str

@dataclass
class DaySchedule:
    """Schedule for one day in the 4‑on/4‑off cycle."""
    title: str
    activities: List[Activity]


def parse_schedule(data: Dict[str, Dict]) -> Dict[str, DaySchedule]:
    """Parse a raw schedule dict into structured ``DaySchedule`` objects."""
    parsed: Dict[str, DaySchedule] = {}
    for day, info in data.items():
        acts = [Activity(*act) for act in info.get("activities", [])]
        parsed[day] = DaySchedule(title=info.get("title", f"Day {day}"), activities=acts)
    return parsed
