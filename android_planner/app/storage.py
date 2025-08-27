"""Persistence helpers for the planner app."""
import json
from pathlib import Path
from typing import Dict

from kivy.app import App

DEFAULT_FILE = Path(__file__).with_name("default_schedule.json")


def _data_dir() -> Path:
    """Return the directory where user data is stored."""
    app = App.get_running_app()
    data_dir = Path(app.user_data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_data() -> Dict:
    """Load schedule data, seeding from the bundled default if missing."""
    data_dir = _data_dir()
    schedule_file = data_dir / "schedule.json"
    if schedule_file.exists():
        with schedule_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    with DEFAULT_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    save_data(data)
    return data


def save_data(data: Dict) -> None:
    """Persist schedule data to disk."""
    data_dir = _data_dir()
    schedule_file = data_dir / "schedule.json"
    with schedule_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)
