import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog, filedialog
import datetime
import json  # For saving and loading data
import calendar  # For the yearly calendar


class ScheduleApp:
    """A modern 4‑on / 4‑off planner tailored for Intel technicians.

    Features
    --------
    ▸ Notebook tabs – each off‑day on its own tab with colour‑coded Treeview rows.
    ▸ Cycle calculator – enter the first off‑day date and get the next 8‑day block mapped.
    ▸ Dark‑mode toggle – instant light/dark switch.
    ▸ Personal notes – quick scratch‑pad area.
    ▸ Save/Load schedule and notes.
    ▸ Edit activities in the schedule.
    ▸ Graphical yearly calendar for on/off cycles.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Intel Technician Off‑Days Schedule")
        self.root.geometry("1000x750")
        self.dark_mode = False
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
        self.on_cycle_color_light = "#FFD3D3"  # Lighter Pink/Red
        self.off_cycle_color_light = "#D3FFD3"  # Lighter Green
        self.on_cycle_color_dark = "#A06060"  # Darker, less saturated Red
        self.off_cycle_color_dark = "#60A060"  # Darker, less saturated Green
        self.other_month_day_fg_light = "#b0b0b0"
        self.other_month_day_fg_dark = "#707070"
        self.today_highlight_bg = "#FFFACD"  # LemonChiffon for light
        self.today_highlight_bg_dark = "#55502A"  # Darker yellow for dark

        # ── ttk theme setup ──────────────────────────────────────────────────────
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._set_light_palette()

        # ── Build and populate UI ───────────────────────────────────────────────
        self._build_widgets()
        self._create_schedule_data()
        self._populate_notebook()
        self.default_notes = "This is a scratchpad for any notes you want to keep."  # Initialize default notes
        self.notes_text.insert("1.0", self.default_notes)

    def _build_widgets(self):
        tk.Label(self.root, text="Intel Technician • 4‑On / 4‑Off Planner", font=self.title_font) \
            .pack(pady=(15, 5))

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=20, pady=5)

        date_calc_frame = ttk.Frame(top_frame)
        date_calc_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(date_calc_frame, text="Current off‑cycle start date (MM/DD/YYYY):") \
            .pack(side=tk.LEFT, padx=(0, 8))
        self.date_entry = ttk.Entry(date_calc_frame, width=12, font=self.normal_font)
        self.date_entry.insert(0, datetime.date.today().strftime("%m/%d/%Y"))
        self.date_entry.pack(side=tk.LEFT)
        ttk.Button(date_calc_frame, text="Calculate Cycle", command=self.calculate_dates).pack(side=tk.LEFT, padx=10)
        theme_button = ttk.Button(top_frame, text="Toggle Dark Mode", command=self.toggle_theme)
        theme_button.pack(side=tk.RIGHT)

        file_ops_frame = ttk.Frame(self.root)
        file_ops_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(file_ops_frame, text="Save Schedule", command=self.save_schedule_dialog).pack(side=tk.LEFT,
                                                                                                 padx=(0, 5))
        ttk.Button(file_ops_frame, text="Save Schedule As...",
                   command=lambda: self.save_schedule_dialog(force_dialog=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Load Schedule", command=self.load_schedule_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="View Yearly Calendar", command=self.show_yearly_calendar).pack(side=tk.LEFT,
                                                                                                        padx=5)

        self.results = tk.Text(self.root, height=3, font=self.small_font, state="disabled", relief=tk.FLAT)
        self.results.pack(fill=tk.X, padx=20, pady=(5, 10))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20)

        legend = ttk.Frame(self.root)
        legend.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(legend, text="Legend:", font=self.small_font).pack(side=tk.LEFT, padx=(0, 6))
        self.legend_item_frames = {}  # To store legend color frames and labels for theme updates
        for name, col in self.colors.items():
            color_frame = tk.Frame(legend, bg=col, width=16, height=16, relief=tk.SUNKEN, borderwidth=1)
            color_frame.pack(side=tk.LEFT)
            label = ttk.Label(legend, text=name.capitalize())
            label.pack(side=tk.LEFT, padx=(4, 8))
            self.legend_item_frames[name] = (color_frame, label)

        notes_frame = ttk.Frame(self.root)
        notes_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 10), expand=True)  # Expand notes section
        ttk.Label(notes_frame, text="Personal Notes:", font=self.header_font).pack(anchor=tk.W, pady=(0, 4))
        self.notes_text = tk.Text(notes_frame, height=4, font=self.small_font, undo=True)  # Enable undo
        self.notes_text.pack(fill=tk.BOTH, expand=True)

    def _create_schedule_data(self):
        self.schedule = {
            "1": {"title": "Recovery after Night Shift", "activities": [
                ["10:00 AM", "Sleep (post‑shift, until ≈3:30 PM)", "sleep"], ["3:30 PM", "Wake up", "morning"],
                ["4:00 PM", "Protein‑rich meal", "meal"], ["4:30 PM", "Take medicine (after meal)", "medicine"],
                ["5:00 PM", "Light stretching / mobility", "morning"], ["5:30 PM", "Grocery shopping", "afternoon"],
                ["7:00 PM", "Pre‑workout snack", "meal"], ["8:00 PM", "Gym – Chest & Triceps", "gym"],
                ["10:00 PM", "Post‑workout meal", "meal"], ["10:30 PM", "Take medicine (after meal)", "medicine"],
                ["11:00 PM", "Relaxation", "evening"], ["12:30 AM", "Bedtime", "evening"],
            ]},
            "2": {"title": "Productive Focus", "activities": [
                ["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Protein breakfast", "meal"],
                ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                ["10:45 AM", "Home maintenance / cleaning", "morning"],
                ["12:30 PM", "Lunch", "meal"], ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                ["1:30 PM", "Deep coding session (2–3 h)", "coding"],
                ["4:30 PM", "Learning – online course", "afternoon"],
                ["5:30 PM", "Rest / pre‑workout prep", "afternoon"], ["6:00 PM", "Pre‑workout meal", "meal"],
                ["7:00 PM", "Gym – Back & Biceps", "gym"], ["9:00 PM", "Post‑workout dinner", "meal"],
                ["9:30 PM", "Take medicine (after dinner)", "medicine"], ["10:00 PM", "Relaxation", "evening"],
                ["12:00 AM", "Bedtime", "evening"],
            ]},
            "3": {"title": "Balance Day", "activities": [
                ["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Protein breakfast", "meal"],
                ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                ["10:45 AM", "Meal prep for remaining days", "morning"],
                ["12:30 PM", "Lunch", "meal"], ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                ["1:30 PM", "Coding session (2–3 h)", "coding"], ["4:30 PM", "Outdoor hobby / walk", "afternoon"],
                ["5:30 PM", "Rest / pre‑workout prep", "afternoon"], ["6:00 PM", "Pre‑workout snack", "meal"],
                ["7:00 PM", "Gym – Shoulders & Abs", "gym"], ["9:00 PM", "Post‑workout dinner", "meal"],
                ["9:30 PM", "Take medicine (after dinner)", "medicine"], ["10:00 PM", "Reading / downtime", "evening"],
                ["12:00 AM", "Bedtime", "evening"],
            ]},
            "4": {"title": "Social / Rest", "activities": [
                ["9:30 AM", "Wake up", "morning"], ["10:00 AM", "Easy breakfast", "meal"],
                ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                ["11:00 AM", "Laundry & chores", "morning"],
                ["12:30 PM", "Lunch – meet a friend", "meal"], ["1:30 PM", "Free time / errands", "afternoon"],
                ["4:30 PM", "Prep for upcoming work block", "afternoon"],
                ["6:00 PM", "Light gym – Stretch & Cardio", "gym"],
                ["7:30 PM", "Cheat‑meal dinner out", "meal"], ["9:00 PM", "Relax with family / friends", "evening"],
                ["11:00 PM", "Early bedtime", "evening"],
            ]},
        }

    def _clear_notebook(self):
        for i in self.notebook.tabs():
            self.notebook.forget(i)

    def _populate_notebook(self):
        self._clear_notebook()
        for day_key, info in sorted(self.schedule.items(), key=lambda item: int(item[0])):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Day {day_key}")
            ttk.Label(tab, text=info["title"], font=self.header_font).pack(anchor=tk.W, pady=(6, 4), padx=6)
            tree = ttk.Treeview(tab, columns=("time", "activity"), show="headings", height=14)
            tree.heading("time", text="Time")
            tree.heading("activity", text="Activity")
            tree.column("time", width=120, anchor=tk.W)
            tree.column("activity", width=670)
            for cat, col in self.colors.items():
                tree.tag_configure(cat, background=col,
                                   foreground=self._get_text_color_for_bg(col))  # Ensure text visibility
            for idx, (t, act, cat) in enumerate(info["activities"]):
                tree.insert("", tk.END, values=(t, act), tags=(cat,), iid=f"day{day_key}_item{idx}")
            tree.bind("<Double-1>", lambda event, d=day_key, t=tree: self.edit_activity_dialog(event, d, t))
            vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
            tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 10))
            tab.treeview = tree

    def _get_text_color_for_bg(self, bg_color):
        """Determine if text should be black or white based on background color luminance."""
        if not bg_color.startswith('#'): return "#000000"  # Default if not hex
        r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#000000" if luminance > 0.5 else "#FFFFFF"

    def edit_activity_dialog(self, event, day_key, tree):
        item_iid = tree.focus()
        if not item_iid: return
        item_values = tree.item(item_iid, "values")
        # IID is "dayX_itemY", we need Y as index
        try:
            item_index_str = item_iid.split("item")[-1]
            item_index = int(item_index_str)
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not identify the item to edit.")
            return

        original_time, original_activity = item_values[0], item_values[1]
        original_category = self.schedule[day_key]["activities"][item_index][2]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Activity")
        dialog.geometry("450x280")  # Slightly wider for category menu
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.style.lookup('TFrame', 'background'))

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

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
            self.schedule[day_key]["activities"][item_index][0] = new_time
            self.schedule[day_key]["activities"][item_index][1] = new_activity
            self.schedule[day_key]["activities"][item_index][2] = new_category
            tree.item(item_iid, values=(new_time, new_activity), tags=(new_category,))
            text_color = self._get_text_color_for_bg(self.colors.get(new_category, "#FFFFFF"))
            tree.tag_configure(new_category, background=self.colors.get(new_category, "#FFFFFF"), foreground=text_color)
            dialog.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=on_save, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        main_frame.grid_columnconfigure(1, weight=1)
        dialog.eval(f'tk::PlaceWindow {str(dialog)} center')  # Center dialog

    def save_schedule_data(self, file_path):
        data_to_save = {
            "schedule": self.schedule,
            "notes": self.notes_text.get("1.0", tk.END).strip(),
            "startDate": self.date_entry.get()
        }
        try:
            with open(file_path, "w") as f:
                json.dump(data_to_save, f, indent=4)
            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path.split('/')[-1]}")
            # messagebox.showinfo("Save Successful", f"Schedule saved to {file_path}") # Optional: less intrusive
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save schedule: {e}")

    def save_schedule_dialog(self, force_dialog=False):
        if not self.current_file_path or force_dialog:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Schedule As"
            )
            if not file_path: return
        else:
            file_path = self.current_file_path
        self.save_schedule_data(file_path)

    def load_schedule_data(self, file_path):
        try:
            with open(file_path, "r") as f:
                loaded_data = json.load(f)
            self.schedule = loaded_data.get("schedule", self._create_schedule_data())
            notes_content = loaded_data.get("notes", self.default_notes)
            start_date = loaded_data.get("startDate", datetime.date.today().strftime("%m/%d/%Y"))
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", notes_content)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, start_date)
            self._populate_notebook()
            self.calculate_dates()
            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path.split('/')[-1]}")
            messagebox.showinfo("Load Successful", f"Schedule loaded from {file_path}")
        except FileNotFoundError:
            messagebox.showerror("Load Error", f"File not found: {file_path}")
            self._create_schedule_data();
            self.notes_text.delete("1.0", tk.END);
            self.notes_text.insert("1.0", self.default_notes);
            self._populate_notebook()
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load schedule: {e}")
            self._create_schedule_data();
            self.notes_text.delete("1.0", tk.END);
            self.notes_text.insert("1.0", self.default_notes);
            self._populate_notebook()

    def load_schedule_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="Load Schedule"
        )
        if file_path: self.load_schedule_data(file_path)

    def calculate_dates(self):
        date_str = self.date_entry.get().strip()
        try:
            self.start_date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()  # Store for calendar
        except ValueError:
            messagebox.showerror("Date Error", "Please enter a valid date in MM/DD/YYYY format.")
            self.start_date_obj = None  # Ensure it's None if invalid
            return
        lines = []
        for i in range(8):
            day = self.start_date_obj + datetime.timedelta(days=i)
            phase = "Off" if i < 4 else "On"
            lines.append(f"{day.strftime('%A, %b %d, %Y')} – {phase} day {i % 4 + 1}")
        self.results.config(state="normal", fg=self.style.lookup('TLabel', 'foreground'))
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "\n".join(lines))
        self.results.config(state="disabled")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self._set_dark_palette()
        else:
            self._set_light_palette()
        if hasattr(self, 'start_date_obj') and self.start_date_obj:  # Check if start_date_obj exists and is valid
            self.calculate_dates()
        self._populate_notebook()  # Re-populate to apply new text colors in treeview

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           YEARLY CALENDAR                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def show_yearly_calendar(self):
        try:
            base_date_str = self.date_entry.get().strip()
            self.base_cycle_start_date_for_calendar = datetime.datetime.strptime(base_date_str, "%m/%d/%Y").date()
        except ValueError:
            messagebox.showerror("Date Error", "Please set a valid 'Current off-cycle start date' (MM/DD/YYYY) first.")
            return

        self.calendar_window = tk.Toplevel(self.root)
        self.calendar_window.title("Yearly Cycle Calendar")
        self.calendar_window.geometry("900x650")
        self.calendar_window.configure(bg=self.style.lookup('TFrame', 'background'))
        self.calendar_window.transient(self.root)
        self.calendar_window.grab_set()

        # Year navigation
        self.calendar_year_var = tk.IntVar(value=datetime.date.today().year)
        nav_frame = ttk.Frame(self.calendar_window)
        nav_frame.pack(pady=10)
        ttk.Button(nav_frame, text="< Prev", command=lambda: self._change_calendar_year(-1)).pack(side=tk.LEFT, padx=5)
        self.year_spinbox = ttk.Spinbox(nav_frame, from_=1900, to=2100, textvariable=self.calendar_year_var, width=6,
                                        command=self._update_calendar_display, font=self.normal_font)
        self.year_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next >", command=lambda: self._change_calendar_year(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Today", command=self._go_to_today_calendar).pack(side=tk.LEFT, padx=20)

        # Legend for calendar
        cal_legend_frame = ttk.Frame(self.calendar_window)
        cal_legend_frame.pack(pady=5)
        on_color = self.on_cycle_color_dark if self.dark_mode else self.on_cycle_color_light
        off_color = self.off_cycle_color_dark if self.dark_mode else self.off_cycle_color_light

        tk.Frame(cal_legend_frame, bg=off_color, width=12, height=12, relief=tk.SUNKEN, borderwidth=1).pack(
            side=tk.LEFT, padx=(0, 2))
        ttk.Label(cal_legend_frame, text="Off-Cycle").pack(side=tk.LEFT, padx=(0, 10))
        tk.Frame(cal_legend_frame, bg=on_color, width=12, height=12, relief=tk.SUNKEN, borderwidth=1).pack(side=tk.LEFT,
                                                                                                           padx=(0, 2))
        ttk.Label(cal_legend_frame, text="On-Cycle").pack(side=tk.LEFT, padx=(0, 10))

        self.calendar_grid_frame = ttk.Frame(self.calendar_window, padding=10)
        self.calendar_grid_frame.pack(expand=True, fill=tk.BOTH)

        self._update_calendar_display()

    def _go_to_today_calendar(self):
        self.calendar_year_var.set(datetime.date.today().year)
        self._update_calendar_display()

    def _change_calendar_year(self, delta):
        self.calendar_year_var.set(self.calendar_year_var.get() + delta)
        self._update_calendar_display()

    def _update_calendar_display(self):
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        year = self.calendar_year_var.get()
        cal = calendar.Calendar(firstweekday=6)  # Sunday as first day

        on_color = self.on_cycle_color_dark if self.dark_mode else self.on_cycle_color_light
        off_color = self.off_cycle_color_dark if self.dark_mode else self.off_cycle_color_light
        text_color = "#FFFFFF" if self.dark_mode else "#000000"
        other_month_fg = self.other_month_day_fg_dark if self.dark_mode else self.other_month_day_fg_light
        today_bg = self.today_highlight_bg_dark if self.dark_mode else self.today_highlight_bg

        # Update legend colors if theme changed while calendar is open
        # (Simple update by repacking legend; could be more refined)
        for widget in self.calendar_window.winfo_children():
            if widget.winfo_class() == 'Frame':  # Check if it's the nav_frame or cal_legend_frame by content
                is_legend = any("Off-Cycle" in child.cget("text") for child in widget.winfo_children() if
                                isinstance(child, ttk.Label))
                if is_legend:
                    for i, child in enumerate(widget.winfo_children()):
                        if isinstance(child, tk.Frame):  # Color swatch
                            if i == 0: child.config(bg=off_color)  # First swatch is Off-cycle
                            if i == 2: child.config(bg=on_color)  # Third swatch is On-cycle
                    break

        cols = 3  # Number of months per row
        for i in range(1, 13):  # For each month
            month_frame = ttk.Frame(self.calendar_grid_frame, relief=tk.SOLID,
                                    borderwidth=0)  # No border for month frame
            month_frame.grid(row=(i - 1) // cols, column=(i - 1) % cols, padx=5, pady=5, sticky="nsew")
            self.calendar_grid_frame.grid_columnconfigure((i - 1) % cols, weight=1)
            self.calendar_grid_frame.grid_rowconfigure((i - 1) // cols, weight=1)

            ttk.Label(month_frame, text=calendar.month_name[i], font=self.calendar_month_font, anchor="center") \
                .grid(row=0, column=0, columnspan=7, pady=(5, 2))

            days_header = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
            for col_idx, day_name in enumerate(days_header):
                ttk.Label(month_frame, text=day_name, font=self.small_font, anchor="center") \
                    .grid(row=1, column=col_idx, sticky="ew", padx=1, pady=1)

            month_days = cal.monthdatescalendar(year, i)
            for week_idx, week in enumerate(month_days):
                for day_idx, day_date_obj in enumerate(week):
                    day_num = day_date_obj.day
                    current_fg = text_color
                    day_bg = self.style.lookup('TFrame', 'background')  # Default bg

                    if day_date_obj.month != i:  # Day not in current month
                        current_fg = other_month_fg
                    else:
                        delta_days = (day_date_obj - self.base_cycle_start_date_for_calendar).days
                        cycle_pos = delta_days % 8  # 0-3 is off, 4-7 is on
                        if 0 <= cycle_pos <= 3:  # Off-cycle
                            day_bg = off_color
                        else:  # On-cycle (4 to 7)
                            day_bg = on_color

                        if day_date_obj == datetime.date.today():
                            day_bg = today_bg  # Override for today

                    day_label = tk.Label(month_frame, text=str(day_num), font=self.calendar_day_font,
                                         bg=day_bg, fg=self._get_text_color_for_bg(
                            day_bg) if day_date_obj.month == i else current_fg,
                                         width=3, height=1, relief=tk.RIDGE,
                                         borderwidth=1 if day_date_obj.month == i else 0)
                    day_label.grid(row=week_idx + 2, column=day_idx, sticky="ew", padx=0.5, pady=0.5)
                    month_frame.grid_columnconfigure(day_idx, weight=1)

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              THEME HELPERS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _apply_palette(self, *, bg: str, fg: str, textbg: str, treefield: str, treehead: str):
        self.root.configure(bg=bg)
        self.style.configure(".", background=bg, foreground=fg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", foreground=fg)  # background often handled by theme
        self.style.map("TButton", background=[('active', bg)], foreground=[('active', fg)])
        self.style.configure("Accent.TButton", foreground=fg,
                             background=self._tint_color(treehead, 0.8))  # Example accent
        self.style.map("Accent.TButton", background=[('active', self._tint_color(treehead, 0.6))])

        self.style.configure("TFrame", background=bg)
        self.style.configure("TNotebook", background=bg)
        self.style.configure("TNotebook.Tab", background=bg, foreground=fg)
        self.style.map("TNotebook.Tab", background=[("selected", treehead)],
                       foreground=[("selected", self._get_text_color_for_bg(treehead))])
        self.style.configure("TSpinbox", fieldbackground=textbg, foreground=fg, background=bg, arrowcolor=fg)

        if hasattr(self, 'results'):
            self.results.configure(bg=textbg, fg=fg, insertbackground=fg, relief=tk.FLAT)
        if hasattr(self, 'notes_text'):
            self.notes_text.configure(bg=textbg, fg=fg, insertbackground=fg)

        # Main title (tk.Label)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label) and widget.master == self.root:  # Only direct children tk.Labels
                widget.configure(bg=bg, fg=fg)

        # Update legend colors
        if hasattr(self, 'legend_item_frames'):
            for name, (color_frame, label_widget) in self.legend_item_frames.items():
                # color_frame background is fixed by self.colors
                label_widget.configure(background=bg, foreground=fg)  # Label bg/fg follows theme

        self.style.configure("Treeview", background=treefield, fieldbackground=treefield, foreground=fg)
        self.style.configure("Treeview.Heading", background=treehead, foreground=self._get_text_color_for_bg(treehead),
                             font=self.small_font)
        self.style.map("Treeview", background=[("selected", "#6A9FB5")],
                       foreground=[("selected", self._get_text_color_for_bg("#6A9FB5"))])

        # If calendar window is open, update its theme too
        if hasattr(self, 'calendar_window') and self.calendar_window.winfo_exists():
            self.calendar_window.configure(bg=bg)
            self._update_calendar_display()  # Redraw calendar with new theme colors

    def _tint_color(self, color_hex, factor):
        """Tints a hex color by a factor. Factor > 1 lightens, < 1 darkens."""
        if not color_hex.startswith('#'): return color_hex
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _set_light_palette(self):
        self._apply_palette(bg="#f0f0f0", fg="#000000", textbg="#ffffff", treefield="#ffffff", treehead="#e1e1e1")

    def _set_dark_palette(self):
        self._apply_palette(bg="#2d2d2d", fg="#ffffff", textbg="#3a3a3a", treefield="#3a3a3a", treehead="#444444")


if __name__ == "__main__":
    root = tk.Tk()
    # Add an accent style for buttons if not present in all themes
    s = ttk.Style()
    s.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

    app = ScheduleApp(root)
    root.mainloop()