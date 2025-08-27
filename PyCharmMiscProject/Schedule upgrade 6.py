import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog, filedialog
import datetime
import json  # For saving and loading data
import calendar  # For the yearly calendar


class ScheduleApp:
    """A modern 4-on / 4-off planner tailored for Intel technicians.

    Features
    --------
    ▸ Notebook tabs – each off-day on its own tab with colour-coded Treeview rows.
    ▸ Cycle calculator – enter the first off-day date and get the next 8-day block mapped.
    ▸ Dark-mode toggle – instant light/dark switch.
    ▸ Personal notes – quick scratch-pad area.
    ▸ Save/Load schedule and notes.
    ▸ Edit activities in the schedule.
    ▸ Graphical yearly calendar for on/off cycles.
    ▸ Clear notes easily.
    ▸ Delete selected activities.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Intel Technician Off-Days Schedule")
        self.root.geometry("1000x750")
        self.dark_mode = False
        self.user_name = ""
        self.current_file_path = None

        # ── Fonts ────────────────────────────────────────────────────────────────
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=12)
        self.small_font = font.Font(family="Helvetica", size=10)
        self.calendar_day_font = font.Font(family="Helvetica", size=9)
        self.calendar_month_font = font.Font(family="Helvetica", size=11, weight="bold")

        # ── Category colours ────────────────────────────────────────────────────
        self.colors = {
            "sleep": "#D0E8FF", "morning": "#CFF5E7", "afternoon": "#FFE5B4",
            "evening": "#FFC1C1", "medicine": "#F7B5B8", "gym": "#E0D4FD",
            "coding": "#C7E6FF", "meal": "#FFF8B8",
        }
        # Colors for yearly calendar
        self.on_cycle_color_light = "#FFD3D3"
        self.off_cycle_color_light = "#D3FFD3"
        self.on_cycle_color_dark = "#A06060"
        self.off_cycle_color_dark = "#60A060"
        self.other_month_day_fg_light = "#b0b0b0"
        self.other_month_day_fg_dark = "#707070"
        self.today_highlight_bg = "#FFFACD"
        self.today_highlight_bg_dark = "#55502A"

        # ── ttk theme setup ──────────────────────────────────────────────────────
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._set_light_palette()

        # ── Build and populate UI ───────────────────────────────────────────────
        self._build_widgets()
        self._create_schedule_data()
        self._populate_notebook()
        self.default_notes = "This is a scratchpad for any notes you want to keep."
        self.notes_text.insert("1.0", self.default_notes)

    def _set_light_palette(self):
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='black')
        self.style.configure('TNotebook', background='white')
        self.style.configure('TNotebook.Tab', background='#e0e0e0', foreground='black')
        self.style.configure('TFrame', background='white')
        self.root.configure(bg='white')

    def _set_dark_palette(self):
        self.style.configure('Treeview', background='#2e2e2e', fieldbackground='#2e2e2e', foreground='white')
        self.style.configure('TNotebook', background='#2e2e2e')
        self.style.configure('TNotebook.Tab', background='#444444', foreground='white')
        self.style.configure('TFrame', background='#2e2e2e')
        self.root.configure(bg='#2e2e2e')

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self._set_dark_palette()
        else:
            self._set_light_palette()

    def _build_widgets(self):
        self.title_label = tk.Label(self.root, text="Intel Technician • 4-On / 4-Off Planner", font=self.title_font)
        self.title_label.pack(pady=(15, 5))
        # Additional widget construction: date entry, buttons, notebook, notes, legend
        # ...

    def _create_schedule_data(self):
        # Initialize schedule dict as before
        self.schedule = {...}

    def _populate_notebook(self):
        # Clear and fill notebook tabs
        pass

    def calculate_dates(self):
        # Cycle calculator implementation
        pass

    def save_schedule_dialog(self, force_dialog=False):
        # Save to JSON
        pass

    def load_schedule_dialog(self):
        # Load from JSON
        pass

    def show_yearly_calendar(self):
        # Display calendar
        pass

    def edit_activity_dialog(self, event, day, tree):
        # Edit activity logic
        pass

    def delete_activity(self, day_key, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Delete Activity", "Please select an activity to delete.")
            return
        item_iid = selected[0]
        idx = int(item_iid.split("item")[-1])
        if messagebox.askyesno("Confirm Delete", "Delete the selected activity?"):
            del self.schedule[day_key]["activities"][idx]
            self._populate_notebook()

    def clear_notes(self):
        if messagebox.askyesno("Clear Notes", "Are you sure you want to clear all notes?"):
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", self.default_notes)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()
