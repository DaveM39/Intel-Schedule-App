"""KivyMD port of the Intel 4-on / 4-off planner.

This is a simplified skeleton of the original Tkinter application. It
provides a tabbed schedule view, cycle calculator, notes field and basic
persistence. The code is structured so it can be expanded to reach full
feature parity with the desktop version.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.picker import MDDatePicker

from app import storage, models
from app.views.tabs import DayTab
from app.views.dialogs import ActivityEditDialog


class PlannerApp(MDApp):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data: Dict[str, Any] = {}
        self.title_text = "4-On / 4-Off Planner"

    def build(self):
        Builder.load_file(Path(__file__).with_name("planner.kv"))
        self.data = storage.load_data()
        user_name = self.data.get("userName", "")
        if user_name:
            self.title_text = f"{user_name} • 4-On / 4-Off Planner"
        return Builder.get_object("MainScreen")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_start(self):
        self.populate_tabs()
        self.root.ids.notes_field.text = self.data.get("notes", "")
        self.root.ids.start_date.text = self.data.get("startDate", "")
        if self.data.get("startDate"):
            self.calculate_cycle()

    # ------------------------------------------------------------------
    # Tabs / schedule
    # ------------------------------------------------------------------
    def populate_tabs(self):
        tabs = self.root.ids.tabs
        tabs.clear_widgets()
        schedule = self.data.get("schedule", {})
        for day, info in sorted(schedule.items(), key=lambda item: int(item[0])):
            tab = DayTab(day_key=str(day), title=info.get("title", f"Day {day}"))
            rv = tab.ids.rv
            rv.data = [
                {
                    "time": act[0],
                    "description": act[1],
                    "category": act[2],
                    "day_key": str(day),
                    "index": idx,
                }
                for idx, act in enumerate(info.get("activities", []))
            ]
            tabs.add_widget(tab)

    def edit_activity(self, day_key: str, index: int):
        activity = self.data["schedule"][day_key]["activities"][index]
        dialog = ActivityEditDialog(
            time=activity[0],
            description=activity[1],
            category=activity[2],
            callback=lambda t, d, c: self._save_activity(day_key, index, t, d, c),
        )
        dialog.open()

    def _save_activity(self, day_key: str, index: int, time: str, desc: str, cat: str):
        self.data["schedule"][day_key]["activities"][index] = [time, desc, cat]
        storage.save_data(self.data)
        self.populate_tabs()

    # ------------------------------------------------------------------
    # Notes / name / theme
    # ------------------------------------------------------------------
    def on_notes_changed(self, text: str):
        self.data["notes"] = text
        storage.save_data(self.data)

    def set_name(self):
        field = MDTextField(text=self.data.get("userName", ""), hint_text="Your name")
        dialog = MDDialog(
            title="Set Name",
            type="custom",
            content_cls=field,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda *_: dialog.dismiss()),
                MDFlatButton(text="Save", on_release=lambda *_: self._save_name(field.text, dialog)),
            ],
        )
        dialog.open()

    def _save_name(self, name: str, dialog: MDDialog):
        dialog.dismiss()
        self.data["userName"] = name
        storage.save_data(self.data)
        self.title_text = f"{name} • 4-On / 4-Off Planner" if name else "4-On / 4-Off Planner"
        self.root.ids.toolbar.title = self.title_text

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"

    # ------------------------------------------------------------------
    # Cycle calculation
    # ------------------------------------------------------------------
    def open_date_picker(self, *_):
        MDDatePicker(callback=self._on_date_selected).open()

    def _on_date_selected(self, date_obj):
        self.root.ids.start_date.text = date_obj.strftime("%Y-%m-%d")
        self.data["startDate"] = self.root.ids.start_date.text
        storage.save_data(self.data)
        self.calculate_cycle()

    def calculate_cycle(self):
        start_str = self.root.ids.start_date.text
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            self.root.ids.results.text = "Invalid date"
            return
        lines = []
        for i in range(8):
            day = start_date + timedelta(days=i)
            status = "Off" if i < 4 else "On"
            lines.append(f"{day:%a %b %d} - {status}")
        self.root.ids.results.text = "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_schedule(self):
        storage.save_data(self.data)

    def load_schedule(self):
        self.data = storage.load_data()
        self.on_start()

    # ------------------------------------------------------------------
    # Colours
    # ------------------------------------------------------------------
    def get_category_rgba(self, category: str):
        hex_col = models.CATEGORY_COLORS.get(category, "#FFFFFF")
        rgba = tuple(int(hex_col[i : i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)
        return rgba


if __name__ == "__main__":
    PlannerApp().run()
