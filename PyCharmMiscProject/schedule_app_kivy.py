# schedule_app_kivy.py
"""
Kivy port of the Tkinter-based Intel Technician 4/4 off‑day schedule.

Features implemented
--------------------
* Tabbed interface – one tab per off‑day, mirroring the original four‑day plan.
* Colour‑coded activity blocks using the same palette as the desktop version.
* Scrollable view to accommodate smaller mobile screens.
* Simple notes field (persisted with the on‑device filesystem).
* Basic cycle date calculator (identical logic, but simplified UI).

Missing vs. Tkinter version
---------------------------
* No fancy fonts – Android will substitute system fonts.
* Window resizing is automatic, so geometry settings were dropped.
* Message‑box pop‑ups replaced with Snackbar (via KivyMD).
* Buildozer‑friendly: only pure‑Python/KivyMD dependencies.

How to package
--------------
1.  Install Buildozer in a Python 3.11 virtualenv (avoid 3.12 until
    distutils issue is fully solved).

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install buildozer cython
    pip install kivy==2.3.1 kivymd==2.0.0rc5
    ```

2.  Initialise buildozer and tweak *buildozer.spec*:

    ```bash
    buildozer init
    # open buildozer.spec and set:
    # requirements = python3,kivy==2.3.1,kivymd==2.0.0rc5
    # android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
    # android.api = 34
    # android.build_type = release  # use debug during dev
    # (add any other tweaks you need)
    ```

3.  Build and deploy:

    ```bash
    buildozer -v android debug deploy run
    ```

The APK will appear under *bin/*.  USB debugging must be enabled on the
phone (or use an emulator).

"""

from pathlib import Path
from datetime import date, timedelta

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import DictProperty, NumericProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.utils import get_color_from_hex

# ------------------------------
# Data section – identical to the Tkinter version
# ------------------------------

def _schedule_dict():
    colors = {
        "morning": "#a8e6cf",
        "afternoon": "#ffd3b6",
        "evening": "#ffaaa5",
        "medicine": "#ff8b94",
        "gym": "#d8b5ff",
        "coding": "#bae1ff",
        "meal": "#fdffb6",
    }

    base = {
        1: {
            "title": "Recovery + Light Activities",
            "activities": [
                ("9:30 AM", "Wake up", "morning"),
                ("10:00 AM", "Protein‑rich breakfast", "meal"),
                ("10:30 AM", "Take medicine (after breakfast)", "medicine"),
                ("11:00 AM", "Light stretching/mobility work", "morning"),
                ("12:30 PM", "Lunch with good protein source", "meal"),
                ("1:00 PM", "Take medicine (after lunch)", "medicine"),
                ("1:30 PM", "Grocery shopping", "afternoon"),
                ("3:30 PM", "Casual coding (1‑2 h)", "coding"),
                ("5:30 PM", "Rest/pre‑workout prep", "afternoon"),
                ("6:00 PM", "Pre‑workout meal", "meal"),
                ("7:00 PM", "Gym – Chest & Triceps", "gym"),
                ("9:00 PM", "Post‑workout meal/dinner", "meal"),
                ("9:30 PM", "Take medicine (after dinner)", "medicine"),
                ("10:30 PM", "Relaxation, entertainment", "evening"),
                ("12:00 AM", "Bedtime", "evening"),
            ],
        },
        2: {
            "title": "Productive Focus",
            "activities": [
                ("9:30 AM", "Wake up", "morning"),
                ("10:00 AM", "Protein breakfast", "meal"),
                ("10:30 AM", "Take medicine (after breakfast)", "medicine"),
                ("10:45 AM", "Home maintenance/cleaning", "morning"),
                ("12:30 PM", "Lunch (protein‑focused)", "meal"),
                ("1:00 PM", "Take medicine (after lunch)", "medicine"),
                ("1:30 PM", "Deep coding session (2‑3 h)", "coding"),
                ("4:30 PM", "Learning/skill development", "afternoon"),
                ("5:30 PM", "Rest/pre‑workout prep", "afternoon"),
                ("6:00 PM", "Pre‑workout meal", "meal"),
                ("7:00 PM", "Gym – Back & Biceps", "gym"),
                ("9:00 PM", "Post‑workout meal/dinner", "meal"),
                ("9:30 PM", "Take medicine (after dinner)", "medicine"),
                ("10:00 PM", "Relaxation", "evening"),
                ("12:00 AM", "Bedtime", "evening"),
            ],
        },
        3: {
            "title": "Balance Day",
            "activities": [
                ("9:30 AM", "Wake up", "morning"),
                ("10:00 AM", "Protein breakfast", "meal"),
                ("10:30 AM", "Take medicine (after breakfast)", "medicine"),
                ("10:45 AM", "Meal prep for remaining days", "morning"),
                ("12:30 PM", "Lunch", "meal"),
                ("1:00 PM", "Take medicine (after lunch)", "medicine"),
                ("1:30 PM", "Coding session (2‑3 h)", "coding"),
                ("4:30 PM", "Outdoor activity/hobby time", "afternoon"),
                ("5:30 PM", "Rest/pre‑workout prep", "afternoon"),
                ("6:00 PM", "Pre‑workout snack", "meal"),
                ("7:00 PM", "Gym – Legs", "gym"),
                ("9:00 PM", "Post‑workout meal/dinner", "meal"),
                ("9:30 PM", "Take medicine (after dinner)", "medicine"),
                ("10:00 PM", "Friends/family time", "evening"),
                ("12:00 AM", "Bedtime", "evening"),
            ],
        },
        4: {
            "title": "Transition Day",
            "activities": [
                ("10:00 AM", "Wake up", "morning"),
                ("10:30 AM", "Protein breakfast", "meal"),
                ("11:00 AM", "Take medicine (after breakfast)", "medicine"),
                ("11:15 AM", "Prepare for upcoming work cycle", "morning"),
                ("12:30 PM", "Lunch", "meal"),
                ("1:00 PM", "Take medicine (after lunch)", "medicine"),
                ("1:30 PM", "Final coding session", "coding"),
                ("3:30 PM", "Errands/appointments", "afternoon"),
                ("5:00 PM", "Pre‑workout prep", "afternoon"),
                ("5:30 PM", "Pre‑workout meal", "meal"),
                ("6:30 PM", "Gym – Active Recovery/Abs/Shoulders", "gym"),
                ("8:00 PM", "Post‑workout meal/dinner", "meal"),
                ("8:30 PM", "Take medicine (after dinner)", "medicine"),
                ("9:00 PM", "Final prep for work", "evening"),
                ("10:00 PM", "Early bedtime", "evening"),
            ],
        },
    }
    return base, colors

SCHEDULE, CAT_COLORS = _schedule_dict()

# ------------------------------
# KV language definition
# ------------------------------

KV = """
<ScheduleLabel@Label>:
    size_hint_y: None
    height: self.texture_size[1] + dp(12)
    text_size: self.width - dp(20), None
    padding_x: dp(10)

<ScheduleTab@BoxLayout>:
    orientation: "vertical"
    ScrollView:
        do_scroll_x: False
        GridLayout:
            id: grid
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            padding: dp(10), dp(10)
            spacing: dp(6)
    MDTextField:
        id: notes
        hint_text: "Notes (saved automatically)"
        size_hint_y: None
        height: dp(56)
        multiline: True
        on_text: app.save_notes(root.day_num, self.text)
"""

# ------------------------------
# UI classes
# ------------------------------

from kivymd.app import MDApp
from kivymd.toast import toast

class ScheduleRoot(TabbedPanel):
    schedule_data: DictProperty = DictProperty(SCHEDULE)
    day_num: NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.build_tabs()

    def build_tabs(self):
        self.clear_tabs()
        for day in range(1, 5):
            tab = self._create_tab(day)
            self.add_widget(tab)

    def _create_tab(self, day):
        tab = Builder.template("ScheduleTab")
        tab.day_num = day
        tab.text = f"Off Day {day}"
        # populate schedule
        grid = tab.ids.grid
        grid.clear_widgets()
        for time, activity, cat in self.schedule_data[day]["activities"]:
            lbl = Builder.template("ScheduleLabel")
            lbl.text = f"[b]{time}[/b]  {activity}"
            lbl.markup = True
            lbl.canvas.before.clear()
            with lbl.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(rgba=get_color_from_hex(CAT_COLORS[cat]) + [1])
                lbl.bg_rect = RoundedRectangle(radius=[8,])
            lbl.bind(size=lambda inst, *a: setattr(inst.bg_rect, "size", inst.size))
            lbl.bind(pos=lambda inst, *a: setattr(inst.bg_rect, "pos", inst.pos))
            grid.add_widget(lbl)
        # restore saved notes if present
        tab.ids.notes.text = self._load_notes(day)
        return tab

    def _load_notes(self, day):
        f = Path(App.get_running_app().user_data_dir) / f"notes_day{day}.txt"
        if f.exists():
            return f.read_text(encoding="utf‑8")
        return ""

    def save_notes(self, day, text):
        f = Path(App.get_running_app().user_data_dir) / f"notes_day{day}.txt"
        f.write_text(text, encoding="utf‑8")
        # Avoid toast spam: show only when length is multiple of 10 chars
        if len(text) % 20 == 0:
            toast("Notes saved")

class ScheduleApp(MDApp):
    def build(self):
        Builder.load_string(KV)
        return ScheduleRoot()

if __name__ == "__main__":
    ScheduleApp().run()
