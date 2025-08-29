import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import datetime
import json
import calendar
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


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
    ▸ Interactive legend for filtering activities with visual feedback.
    """

    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("Intel Technician Off-Days Schedule")
        self.root.geometry("1000x850")
        self.dark_mode = False
        self.user_name = ""
        self.title_label = None
        self.current_file_path = None
        self.active_filter = None
        self.legend_labels = {}
        self.legend_swatches = {}

        # ── Fonts ────────────────────────────────────────────────────────────────
        self.title_font = ("Helvetica", 18, "bold")
        self.header_font = ("Helvetica", 14, "bold")
        self.normal_font = ("Helvetica", 12)
        self.small_font = ("Helvetica", 10)
        self.legend_font_normal = ("Helvetica", 10)
        self.legend_font_bold = ("Helvetica", 10, "bold")
        self.swatch_font = ("Helvetica", 10, "bold")
        self.calendar_day_font = ("Helvetica", 9)
        self.calendar_month_font = ("Helvetica", 11, "bold")

        # ── Category colours ────────────────────────────────────────────────────
        self.colors = {
            "sleep": "#D0E8FF", "morning": "#CFF5E7", "afternoon": "#FFE5B4",
            "evening": "#FFC1C1", "medicine": "#F7B5B8", "gym": "#E0D4FD",
            "coding": "#C7E6FF", "meal": "#FFF8B8",
        }
        self.on_cycle_color_light = "#FFD3D3"
        self.off_cycle_color_light = "#D3FFD3"
        self.on_cycle_color_dark = "#A06060"
        self.off_cycle_color_dark = "#60A060"
        self.other_month_day_fg_light = "#b0b0b0"
        self.other_month_day_fg_dark = "#707070"
        self.today_highlight_bg = "#FFFACD"
        self.today_highlight_bg_dark = "#55502A"

        # ── Build and populate UI ───────────────────────────────────────────────
        self._build_widgets()
        self._create_schedule_data()
        self._populate_notebook()
        self.default_notes = "This is a scratchpad for any notes you want to keep."
        self.notes_text.insert("1.0", self.default_notes)
        self.calculate_dates()

    def _build_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        self.title_label = ttk.Label(main_frame, text="Intel Technician • 4‑On / 4‑Off Planner", font=self.title_font,
                                     bootstyle="primary")
        self.title_label.pack(pady=(0, 15))

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=X, pady=5)

        date_calc_frame = ttk.Frame(top_frame)
        date_calc_frame.pack(side=LEFT, fill=X, expand=YES)
        ttk.Label(date_calc_frame, text="Current off-cycle start date:").pack(side=LEFT, padx=(0, 8))

        self.date_entry = ttk.DateEntry(date_calc_frame, bootstyle="primary", dateformat="%m/%d/%Y")
        self.date_entry.entry.insert(0, datetime.date.today().strftime("%m/%d/%Y"))
        self.date_entry.pack(side=LEFT)

        ttk.Button(date_calc_frame, text="Calculate Cycle", command=self.calculate_dates,
                   bootstyle="primary-outline").pack(side=LEFT, padx=10)

        theme_button = ttk.Button(top_frame, text="Toggle Dark Mode", command=self.toggle_theme,
                                  bootstyle="info-outline")
        theme_button.pack(side=RIGHT)
        ttk.Button(top_frame, text="Set Name", command=self.set_user_name, bootstyle="secondary-outline").pack(
            side=RIGHT, padx=10)

        file_ops_frame = ttk.Frame(main_frame)
        file_ops_frame.pack(fill=X, pady=10)
        ttk.Button(file_ops_frame, text="Save", command=self.save_schedule_dialog, bootstyle="success-outline").pack(
            side=LEFT, padx=(0, 5))
        ttk.Button(file_ops_frame, text="Save As...", command=lambda: self.save_schedule_dialog(force_dialog=True),
                   bootstyle="success-outline").pack(side=LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Load", command=self.load_schedule_dialog, bootstyle="warning-outline").pack(
            side=LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Yearly Calendar", command=self.show_yearly_calendar,
                   bootstyle="info-outline").pack(side=LEFT, padx=5)

        self.results = tk.Text(main_frame, height=9, font=self.small_font, relief=FLAT, state="disabled")
        self.results.pack(fill=X, pady=(5, 10))

        self.notebook = ttk.Notebook(main_frame, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES)

        self._build_legend(main_frame)

        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=BOTH, pady=(10, 0), expand=YES)
        ttk.Label(notes_frame, text="Personal Notes:", font=self.header_font, bootstyle="primary").pack(anchor=W,
                                                                                                        pady=(0, 4))
        self.notes_text = tk.Text(notes_frame, height=4, font=self.small_font, undo=True, relief=FLAT)
        self.notes_text.pack(fill=BOTH, expand=YES)
        self._apply_theme()

    def _build_legend(self, parent):
        """Builds the interactive legend."""
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill=X, pady=8)
        ttk.Label(legend_frame, text="Filter by:", font=self.small_font).pack(side=LEFT, padx=(0, 6))

        self.legend_labels = {}
        self.legend_swatches = {}
        for name, col in self.colors.items():
            swatch = ttk.Label(legend_frame, text="", background=col, width=2,
                               relief=SUNKEN, borderwidth=1, cursor="hand2",
                               anchor=CENTER, font=self.swatch_font)
            swatch.pack(side=LEFT)
            swatch.bind("<Button-1>", lambda e, n=name: self.filter_by_category(n))
            self.legend_swatches[name] = swatch

            label = ttk.Label(legend_frame, text=name.capitalize(), cursor="hand2", font=self.legend_font_normal,
                              padding=(5, 2))
            label.pack(side=LEFT, padx=(4, 8))
            label.bind("<Button-1>", lambda e, n=name: self.filter_by_category(n))
            self.legend_labels[name] = label

        self.clear_filter_button = ttk.Button(legend_frame, text="Clear Filter", command=self.clear_filter,
                                              bootstyle="link-primary")
        self.clear_filter_button.pack(side=LEFT, padx=20)

    def _create_schedule_data(self):
        """Creates the default schedule data."""
        self.schedule = {
            "1": {"title": "Recovery after Night Shift",
                  "activities": [["10:00 AM", "Sleep (post‑shift, until ≈3:30 PM)", "sleep"],
                                 ["3:30 PM", "Wake up", "morning"], ["4:00 PM", "Protein‑rich meal", "meal"],
                                 ["4:30 PM", "Take medicine (after meal)", "medicine"],
                                 ["5:00 PM", "Light stretching / mobility", "morning"],
                                 ["5:30 PM", "Grocery shopping", "afternoon"], ["7:00 PM", "Pre‑workout snack", "meal"],
                                 ["8:00 PM", "Gym – Chest & Triceps", "gym"], ["10:00 PM", "Post‑workout meal", "meal"],
                                 ["10:30 PM", "Take medicine (after meal)", "medicine"],
                                 ["11:00 PM", "Relaxation", "evening"], ["12:30 AM", "Bedtime", "evening"]]},
            "2": {"title": "Productive Focus",
                  "activities": [["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Protein breakfast", "meal"],
                                 ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                                 ["10:45 AM", "Home maintenance / cleaning", "morning"], ["12:30 PM", "Lunch", "meal"],
                                 ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                                 ["1:30 PM", "Deep coding session (2–3 h)", "coding"],
                                 ["4:30 PM", "Learning – online course", "afternoon"],
                                 ["5:30 PM", "Rest / pre‑workout prep", "afternoon"],
                                 ["6:00 PM", "Pre‑workout meal", "meal"], ["7:00 PM", "Gym – Back & Biceps", "gym"],
                                 ["9:00 PM", "Post‑workout dinner", "meal"],
                                 ["9:30 PM", "Take medicine (after dinner)", "medicine"],
                                 ["10:00 PM", "Relaxation", "evening"], ["12:00 AM", "Bedtime", "evening"]]},
            "3": {"title": "Balance Day",
                  "activities": [["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Protein breakfast", "meal"],
                                 ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                                 ["10:45 AM", "Meal prep for remaining days", "morning"], ["12:30 PM", "Lunch", "meal"],
                                 ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                                 ["1:30 PM", "Coding session (2–3 h)", "coding"],
                                 ["4:30 PM", "Outdoor hobby / walk", "afternoon"],
                                 ["5:30 PM", "Rest / pre‑workout prep", "afternoon"],
                                 ["6:00 PM", "Pre‑workout snack", "meal"], ["7:00 PM", "Gym – Shoulders & Abs", "gym"],
                                 ["9:00 PM", "Post‑workout dinner", "meal"],
                                 ["9:30 PM", "Take medicine (after dinner)", "medicine"],
                                 ["10:00 PM", "Reading / downtime", "evening"], ["12:00 AM", "Bedtime", "evening"]]},
            "4": {"title": "Social / Rest",
                  "activities": [["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Easy breakfast", "meal"],
                                 ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                                 ["11:00 AM", "Laundry & chores", "morning"],
                                 ["12:30 PM", "Lunch – meet a friend", "meal"],
                                 ["1:30 PM", "Free time / errands", "afternoon"],
                                 ["4:30 PM", "Prep for upcoming work block", "afternoon"],
                                 ["6:00 PM", "Light gym – Stretch & Cardio", "gym"],
                                 ["7:30 PM", "Cheat‑meal dinner out", "meal"],
                                 ["9:00 PM", "Relax with family / friends", "evening"],
                                 ["11:00 PM", "Early bedtime", "evening"]]}
        }

    def _clear_notebook(self):
        for i in self.notebook.tabs():
            self.notebook.forget(i)

    def _populate_notebook(self):
        """Builds the notebook tabs and populates them with full schedules."""
        self._clear_notebook()
        for day_key, info in sorted(self.schedule.items(), key=lambda item: int(item[0])):
            tab = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(tab, text=f"Day {day_key}")
            tab.day_key = day_key

            ttk.Label(tab, text=info["title"], font=self.header_font, bootstyle="primary").pack(anchor=W, pady=(0, 10))
            tree = ttk.Treeview(tab, columns=("time", "activity"), show="headings", height=14, bootstyle="primary")
            tree.heading("time", text="Time")
            tree.heading("activity", text="Activity")
            tree.column("time", width=120, anchor=W)
            tree.column("activity", width=670)

            for cat, col in self.colors.items():
                tree.tag_configure(cat, background=col, foreground=self._get_text_color_for_bg(col))

            self._rebuild_tree(tree, day_key)

            tree.bind("<Double-1>", lambda event, d=day_key, t=tree: self.edit_activity_dialog(event, d, t))
            vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview, bootstyle="round-primary")
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side=RIGHT, fill=Y)
            tree.pack(fill=BOTH, expand=YES)
            tab.treeview = tree

    def _rebuild_tree(self, tree, day_key, filter_category=None):
        """Helper function to clear and repopulate a tree, optionally filtering."""
        tree.delete(*tree.get_children())

        all_activities = self.schedule[day_key]["activities"]

        activities_to_show = [act for act in all_activities if
                              act[2] == filter_category] if filter_category else all_activities

        for activity in activities_to_show:
            t, act, cat = activity
            original_idx = all_activities.index(activity)
            iid = f"day{day_key}_item{original_idx}"
            tree.insert("", END, values=(t, act), tags=(cat,), iid=iid)

    def _get_text_color_for_bg(self, bg_color):
        if not isinstance(bg_color, str) or not bg_color.startswith('#'): return "#000000"
        try:
            r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return "#000000" if luminance > 0.5 else "#FFFFFF"
        except ValueError:
            return "#000000"

    def edit_activity_dialog(self, event, day_key, tree):
        # This function is unchanged
        item_iid = tree.focus()
        if not item_iid: return
        item_values = tree.item(item_iid, "values")
        try:
            item_index = int(item_iid.split("item")[-1])
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not identify the item to edit.")
            return
        original_time, original_activity = item_values[0], item_values[1]
        original_category = self.schedule[day_key]["activities"][item_index][2]
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Activity")
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(expand=YES, fill=BOTH)
        ttk.Label(main_frame, text="Time:", font=self.normal_font).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        time_entry = ttk.Entry(main_frame, font=self.normal_font, width=35)
        time_entry.insert(0, original_time)
        time_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ttk.Label(main_frame, text="Activity:", font=self.normal_font).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        activity_entry = ttk.Entry(main_frame, font=self.normal_font, width=35)
        activity_entry.insert(0, original_activity)
        activity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(main_frame, text="Category:", font=self.normal_font).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        category_var = tk.StringVar(value=original_category)
        category_menu = ttk.Combobox(main_frame, textvariable=category_var, values=list(self.colors.keys()),
                                     font=self.normal_font, state="readonly", width=33)
        category_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        def on_save():
            new_time = time_entry.get().strip()
            new_activity = activity_entry.get().strip()
            new_category = category_var.get()
            if not new_time or not new_activity or not new_category:
                messagebox.showwarning("Input Error", "Time, Activity, and Category cannot be empty.", parent=dialog)
                return
            self.schedule[day_key]["activities"][item_index] = [new_time, new_activity, new_category]
            self.clear_filter()  # Rebuild tree to show the change
            dialog.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=on_save, bootstyle="success").pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, bootstyle="danger-outline").pack(side=LEFT,
                                                                                                         padx=10)
        main_frame.grid_columnconfigure(1, weight=1)

    # save, load, get_date, calculate_dates functions are unchanged
    def save_schedule_data(self, file_path):
        start_date_str = self.date_entry.entry.get()
        data_to_save = {"schedule": self.schedule, "notes": self.notes_text.get("1.0", END).strip(),
                        "startDate": start_date_str, "userName": self.user_name}
        try:
            with open(file_path, "w") as f:
                json.dump(data_to_save, f, indent=4)
            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save schedule: {e}")

    def save_schedule_dialog(self, force_dialog=False):
        if not self.current_file_path or force_dialog:
            file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                     filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                     title="Save Schedule As")
            if not file_path: return
        else:
            file_path = self.current_file_path
        self.save_schedule_data(file_path)

    def load_schedule_data(self, file_path):
        try:
            with open(file_path, "r") as f:
                loaded_data = json.load(f)
            self.schedule = loaded_data.get("schedule", self._create_schedule_data())
            self.user_name = loaded_data.get("userName", "")
            if self.user_name:
                self.title_label.config(text=f"{self.user_name} • 4-On / 4-Off Planner")
            else:
                self.title_label.config(text="Intel Technician • 4-On / 4-Off Planner")
            notes_content = loaded_data.get("notes", self.default_notes)
            start_date_str = loaded_data.get("startDate", datetime.date.today().strftime("%m/%d/%Y"))
            self.date_entry.entry.delete(0, END)
            self.date_entry.entry.insert(0, start_date_str)
            self.notes_text.delete("1.0", END)
            self.notes_text.insert("1.0", notes_content)
            self._populate_notebook()
            self.calculate_dates()
            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path.split('/')[-1]}")
            messagebox.showinfo("Load Successful", f"Schedule loaded from {file_path}")
        except FileNotFoundError:
            messagebox.showerror("Load Error", f"File not found: {file_path}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load schedule: {e}")

    def load_schedule_dialog(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                               title="Load Schedule")
        if file_path: self.load_schedule_data(file_path)

    def get_date_from_entry(self):
        date_str = self.date_entry.entry.get()
        try:
            return datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            messagebox.showerror("Invalid Date",
                                 f"Please enter a valid date in MM/DD/YYYY format. You entered: {date_str}")
            return None

    def calculate_dates(self):
        self.start_date_obj = self.get_date_from_entry()
        if not self.start_date_obj: return
        lines = []
        for i in range(8):
            day = self.start_date_obj + datetime.timedelta(days=i)
            phase = "Off" if i < 4 else "On"
            lines.append(f"{day.strftime('%A, %b %d, %Y')} – {phase} day {i % 4 + 1}")
        self.results.config(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "\n".join(lines))
        self.results.config(state="disabled")

    def toggle_theme(self):
        self.root.style.theme_use('darkly' if not self.dark_mode else 'litera')
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self.clear_filter()

    def _apply_theme(self):
        style = self.root.style
        bg_color = style.colors.get('bg')
        fg_color = style.colors.get('fg')
        text_bg_color = style.colors.get('inputbg')
        self.results.configure(bg=text_bg_color, fg=fg_color)
        self.notes_text.configure(bg=text_bg_color, fg=fg_color, insertbackground=fg_color)
        if hasattr(self, 'calendar_window') and self.calendar_window.winfo_exists():
            self._update_calendar_display()

    def filter_by_category(self, category_to_filter):
        """Rebuilds the tree with only filtered items."""
        self.active_filter = category_to_filter
        self._update_legend_visuals()
        try:
            selected_tab_widget = self.root.nametowidget(self.notebook.select())
            tree = selected_tab_widget.treeview
            day_key = selected_tab_widget.day_key
            self._rebuild_tree(tree, day_key, filter_category=category_to_filter)
        except (KeyError, AttributeError):
            return

    def clear_filter(self):
        """Rebuilds the tree with all original items."""
        self.active_filter = None
        self._update_legend_visuals()
        try:
            selected_tab_widget = self.root.nametowidget(self.notebook.select())
            tree = selected_tab_widget.treeview
            day_key = selected_tab_widget.day_key
            self._rebuild_tree(tree, day_key, filter_category=None)
        except (KeyError, AttributeError):
            return

    def _update_legend_visuals(self):
        """Bolds the active text and adds a checkmark to the active swatch."""
        for name, label in self.legend_labels.items():
            if name == self.active_filter:
                label.config(font=self.legend_font_bold)
            else:
                label.config(font=self.legend_font_normal)

        for name, swatch in self.legend_swatches.items():
            if name == self.active_filter:
                swatch.config(text="✓", foreground=self._get_text_color_for_bg(self.colors[name]))
            else:
                swatch.config(text="")

    def show_yearly_calendar(self):
        self.base_cycle_start_date_for_calendar = self.get_date_from_entry()
        if not self.base_cycle_start_date_for_calendar:
            return

        self.calendar_window = ttk.Toplevel(self.root)
        self.calendar_window.title("Yearly Cycle Calendar")
        self.calendar_window.geometry("1080x900")

        self.calendar_year_var = tk.IntVar(value=datetime.date.today().year)
        nav_frame = ttk.Frame(self.calendar_window, padding=10)
        nav_frame.pack()
        ttk.Button(nav_frame, text="< Prev", command=lambda: self._change_calendar_year(-1), bootstyle="primary").pack(
            side=LEFT, padx=5)
        self.year_spinbox = ttk.Spinbox(nav_frame, from_=1900, to=2100, textvariable=self.calendar_year_var, width=6,
                                        command=self._update_calendar_display, bootstyle="primary")
        self.year_spinbox.pack(side=LEFT, padx=5)
        ttk.Button(nav_frame, text="Next >", command=lambda: self._change_calendar_year(1), bootstyle="primary").pack(
            side=LEFT, padx=5)
        ttk.Button(nav_frame, text="Today", command=self._go_to_today_calendar, bootstyle="secondary").pack(side=LEFT,
                                                                                                            padx=20)
        cal_legend_frame = ttk.Frame(self.calendar_window, padding=(0, 5))
        cal_legend_frame.pack()
        self.cal_legend_on_swatch = tk.Frame(cal_legend_frame, width=12, height=12, relief=SUNKEN, borderwidth=1)
        self.cal_legend_on_swatch.pack(side=LEFT, padx=(0, 2))
        ttk.Label(cal_legend_frame, text="On-Cycle").pack(side=LEFT, padx=(0, 10))
        self.cal_legend_off_swatch = tk.Frame(cal_legend_frame, width=12, height=12, relief=SUNKEN, borderwidth=1)
        self.cal_legend_off_swatch.pack(side=LEFT, padx=(0, 2))
        ttk.Label(cal_legend_frame, text="Off-Cycle").pack(side=LEFT, padx=(0, 10))
        self.calendar_grid_frame = ttk.Frame(self.calendar_window, padding=10)
        self.calendar_grid_frame.pack(expand=YES, fill=BOTH)

        self._update_calendar_display()

    def _go_to_today_calendar(self):
        self.calendar_year_var.set(datetime.date.today().year)
        self._update_calendar_display()

    def _change_calendar_year(self, delta):
        self.calendar_year_var.set(self.calendar_year_var.get() + delta)
        self._update_calendar_display()

    def _update_calendar_display(self):
        """FIX: Uses a more robust grid layout for day numbers."""
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        year = self.calendar_year_var.get()
        cal = calendar.Calendar(firstweekday=6)

        on_color = self.on_cycle_color_dark if self.dark_mode else self.on_cycle_color_light
        off_color = self.off_cycle_color_dark if self.dark_mode else self.off_cycle_color_light

        style = self.root.style
        bg_color_default = style.colors.get('bg')

        other_month_fg = self.other_month_day_fg_dark if self.dark_mode else self.other_month_day_fg_light
        today_bg = self.today_highlight_bg_dark if self.dark_mode else self.today_highlight_bg

        self.cal_legend_on_swatch.config(bg=on_color)
        self.cal_legend_off_swatch.config(bg=off_color)

        cols = 3
        TARGET_WEEKS_PER_MONTH_DISPLAY = 6

        for i in range(1, 13):
            month_frame = ttk.Frame(self.calendar_grid_frame)
            month_frame.grid(row=(i - 1) // cols, column=(i - 1) % cols, padx=5, pady=5, sticky="nsew")
            self.calendar_grid_frame.grid_columnconfigure((i - 1) % cols, weight=1)
            self.calendar_grid_frame.grid_rowconfigure((i - 1) // cols, weight=1)

            ttk.Label(month_frame, text=calendar.month_name[i], font=self.calendar_month_font, anchor="center").grid(
                row=0, column=0, columnspan=7, pady=(5, 2))
            days_header = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
            for col_idx, day_name in enumerate(days_header):
                ttk.Label(month_frame, text=day_name, font=self.small_font, anchor="center").grid(row=1, column=col_idx,
                                                                                                  sticky="ew", padx=1,
                                                                                                  pady=1)

            month_days = cal.monthdatescalendar(year, i)
            all_days = [day for week in month_days for day in week]
            while len(all_days) < TARGET_WEEKS_PER_MONTH_DISPLAY * 7:
                all_days.append(all_days[-1] + datetime.timedelta(days=1))

            for week_idx in range(TARGET_WEEKS_PER_MONTH_DISPLAY):
                for day_idx in range(7):
                    day_date_obj = all_days[week_idx * 7 + day_idx]
                    day_num = day_date_obj.day

                    day_bg = bg_color_default

                    if day_date_obj.month != i:
                        current_fg = other_month_fg
                    else:
                        delta_days = (day_date_obj - self.base_cycle_start_date_for_calendar).days
                        cycle_pos = delta_days % 8
                        if 0 <= cycle_pos <= 3:
                            day_bg = off_color
                        else:
                            day_bg = on_color
                        if day_date_obj == datetime.date.today(): day_bg = today_bg
                        current_fg = self._get_text_color_for_bg(day_bg)

                    day_frame = tk.Frame(month_frame, background=day_bg)
                    day_frame.grid(row=week_idx + 2, column=day_idx, sticky="nsew", padx=0.5, pady=0.5)
                    day_frame.grid_rowconfigure(0, weight=1)
                    day_frame.grid_columnconfigure(0, weight=1)

                    day_label = ttk.Label(day_frame, text=str(day_num), font=self.calendar_day_font,
                                          foreground=current_fg, background=day_bg, anchor=CENTER)
                    day_label.grid(row=0, column=0, sticky="nsew")

                    month_frame.grid_columnconfigure(day_idx, weight=1)
                month_frame.grid_rowconfigure(week_idx + 2, weight=1)

    def set_user_name(self):
        first = simpledialog.askstring("First name", "Enter your first name:", parent=self.root)
        if first is None: return
        last = simpledialog.askstring("Last name", "Enter your last name:", parent=self.root)
        if last is None: return
        self.user_name = f"{first.strip()} {last.strip()}"
        self.title_label.config(text=f"{self.user_name} • 4-On / 4-Off Planner")


if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = ScheduleApp(root)
    root.mainloop()