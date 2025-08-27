import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog, filedialog
import datetime
import json  # For saving and loading data


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
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Intel Technician Off‑Days Schedule")
        self.root.geometry("1000x750")  # Increased height slightly for new buttons
        self.dark_mode = False
        self.current_file_path = None  # To store path of currently opened file

        # ── Fonts ────────────────────────────────────────────────────────────────
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=12)
        self.small_font = font.Font(family="Helvetica", size=10)

        # ── Category colours ────────────────────────────────────────────────────
        self.colors = {
            "sleep": "#D0E8FF",
            "morning": "#CFF5E7",
            "afternoon": "#FFE5B4",
            "evening": "#FFC1C1",
            "medicine": "#F7B5B8",
            "gym": "#E0D4FD",
            "coding": "#C7E6FF",
            "meal": "#FFF8B8",
        }

        # ── ttk theme setup ──────────────────────────────────────────────────────
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._set_light_palette()

        # ── Build and populate UI ───────────────────────────────────────────────
        self._build_widgets()
        self._create_schedule_data()  # Load default schedule
        self._populate_notebook()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               UI BUILDERS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _build_widgets(self):
        tk.Label(self.root, text="Intel Technician • 4‑On / 4‑Off Planner", font=self.title_font) \
            .pack(pady=(15, 5))

        # Top toolbar
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

        # File Operations Frame
        file_ops_frame = ttk.Frame(self.root)
        file_ops_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(file_ops_frame, text="Save Schedule", command=self.save_schedule_dialog).pack(side=tk.LEFT,
                                                                                                 padx=(0, 5))
        ttk.Button(file_ops_frame, text="Save Schedule As...",
                   command=lambda: self.save_schedule_dialog(force_dialog=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Load Schedule", command=self.load_schedule_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="View Yearly Calendar", command=self.show_yearly_calendar).pack(side=tk.LEFT,
                                                                                                        padx=5)  # Placeholder

        # Results box
        self.results = tk.Text(self.root, height=3, font=self.small_font, state="disabled", relief=tk.FLAT,
                               bg=self.root.cget("bg"))
        self.results.pack(fill=tk.X, padx=20, pady=(5, 10))

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20)

        # Legend
        legend = ttk.Frame(self.root)
        legend.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(legend, text="Legend:", font=self.small_font).pack(side=tk.LEFT, padx=(0, 6))
        for name, col in self.colors.items():
            tk.Frame(legend, bg=col, width=16, height=16).pack(side=tk.LEFT)
            ttk.Label(legend, text=name.capitalize()).pack(side=tk.LEFT, padx=(4, 8))

        # Notes
        notes_frame = ttk.Frame(self.root)
        notes_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 10))
        ttk.Label(notes_frame, text="Personal Notes:", font=self.header_font).pack(anchor=tk.W, pady=(0, 4))
        self.notes_text = tk.Text(notes_frame, height=4, font=self.small_font)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        # Save notes button is removed as notes are saved with the schedule.
        # If you want a separate save notes button, it can be added back.

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                       DATA & NOTEBOOK POPULATION                         ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _create_schedule_data(self):
        """Hard‑coded demo agenda for the 4 off‑days. Day‑1 now begins with post‑night‑shift sleep."""
        self.schedule = {
            "1": {  # Using string keys for JSON compatibility
                "title": "Recovery after Night Shift",
                "activities": [
                    ["10:00 AM", "Sleep (post‑shift, until ≈3:30 PM)", "sleep"],  # Activities are lists now
                    ["3:30 PM", "Wake up", "morning"],
                    ["4:00 PM", "Protein‑rich meal", "meal"],
                    ["4:30 PM", "Take medicine (after meal)", "medicine"],
                    ["5:00 PM", "Light stretching / mobility", "morning"],
                    ["5:30 PM", "Grocery shopping", "afternoon"],
                    ["7:00 PM", "Pre‑workout snack", "meal"],
                    ["8:00 PM", "Gym – Chest & Triceps", "gym"],
                    ["10:00 PM", "Post‑workout meal", "meal"],
                    ["10:30 PM", "Take medicine (after meal)", "medicine"],
                    ["11:00 PM", "Relaxation", "evening"],
                    ["12:30 AM", "Bedtime", "evening"],
                ],
            },
            "2": {
                "title": "Productive Focus",
                "activities": [
                    ["9:30 AM", "Wake up", "morning"],
                    ["10:00 AM", "Protein breakfast", "meal"],
                    ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                    ["10:45 AM", "Home maintenance / cleaning", "morning"],
                    ["12:30 PM", "Lunch", "meal"],
                    ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                    ["1:30 PM", "Deep coding session (2–3 h)", "coding"],
                    ["4:30 PM", "Learning – online course", "afternoon"],
                    ["5:30 PM", "Rest / pre‑workout prep", "afternoon"],
                    ["6:00 PM", "Pre‑workout meal", "meal"],
                    ["7:00 PM", "Gym – Back & Biceps", "gym"],
                    ["9:00 PM", "Post‑workout dinner", "meal"],
                    ["9:30 PM", "Take medicine (after dinner)", "medicine"],
                    ["10:00 PM", "Relaxation", "evening"],
                    ["12:00 AM", "Bedtime", "evening"],
                ],
            },
            "3": {
                "title": "Balance Day",
                "activities": [
                    ["9:30 AM", "Wake up", "morning"],
                    ["10:00 AM", "Protein breakfast", "meal"],
                    ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                    ["10:45 AM", "Meal prep for remaining days", "morning"],
                    ["12:30 PM", "Lunch", "meal"],
                    ["1:00 PM", "Take medicine (after lunch)", "medicine"],
                    ["1:30 PM", "Coding session (2–3 h)", "coding"],
                    ["4:30 PM", "Outdoor hobby / walk", "afternoon"],
                    ["5:30 PM", "Rest / pre‑workout prep", "afternoon"],
                    ["6:00 PM", "Pre‑workout snack", "meal"],
                    ["7:00 PM", "Gym – Shoulders & Abs", "gym"],
                    ["9:00 PM", "Post‑workout dinner", "meal"],
                    ["9:30 PM", "Take medicine (after dinner)", "medicine"],
                    ["10:00 PM", "Reading / downtime", "evening"],
                    ["12:00 AM", "Bedtime", "evening"],
                ],
            },
            "4": {
                "title": "Social / Rest",
                "activities": [
                    ["9:30 AM", "Wake up", "morning"],
                    ["10:00 AM", "Easy breakfast", "meal"],
                    ["10:30 AM", "Take medicine (after breakfast)", "medicine"],
                    ["11:00 AM", "Laundry & chores", "morning"],
                    ["12:30 PM", "Lunch – meet a friend", "meal"],
                    ["1:30 PM", "Free time / errands", "afternoon"],
                    ["4:30 PM", "Prep for upcoming work block", "afternoon"],
                    ["6:00 PM", "Light gym – Stretch & Cardio", "gym"],
                    ["7:30 PM", "Cheat‑meal dinner out", "meal"],
                    ["9:00 PM", "Relax with family / friends", "evening"],
                    ["11:00 PM", "Early bedtime", "evening"],
                ],
            },
        }
        # Default notes
        self.default_notes = "This is a scratchpad for any notes you want to keep."

    def _clear_notebook(self):
        for i in self.notebook.tabs():
            self.notebook.forget(i)

    def _populate_notebook(self):
        self._clear_notebook()  # Clear existing tabs before populating
        for day_key, info in sorted(self.schedule.items(), key=lambda item: int(item[0])):  # Ensure days are sorted
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Day {day_key}")  # Use day_key (string "1", "2" etc)
            ttk.Label(tab, text=info["title"], font=self.header_font).pack(anchor=tk.W, pady=(6, 4), padx=6)

            tree = ttk.Treeview(tab, columns=("time", "activity"), show="headings", height=14)
            tree.heading("time", text="Time")
            tree.heading("activity", text="Activity")
            tree.column("time", width=120, anchor=tk.W)  # Wider for easier editing, anchor W
            tree.column("activity", width=670)  # Adjusted width
            for cat, col in self.colors.items():
                tree.tag_configure(cat, background=col)

            for idx, (t, act, cat) in enumerate(info["activities"]):
                item_id = tree.insert("", tk.END, values=(t, act), tags=(cat,), iid=f"day{day_key}_item{idx}")

            # Bind double click for editing
            tree.bind("<Double-1>", lambda event, d=day_key, t=tree: self.edit_activity_dialog(event, d, t))

            vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
            tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 10))

            # Store tree in tab for easy access if needed later for refresh
            tab.treeview = tree

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            SCHEDULE EDITING                             ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def edit_activity_dialog(self, event, day_key, tree):
        item_iid = tree.focus()  # Get selected item
        if not item_iid:
            return

        item_values = tree.item(item_iid, "values")
        item_index = int(item_iid.split("item")[-1])  # Extract index from IID like "day1_item0"

        original_time, original_activity = item_values[0], item_values[1]
        original_category = self.schedule[day_key]["activities"][item_index][2]  # Get category

        # Create a dialog for editing
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Activity")
        dialog.geometry("400x250")
        dialog.transient(self.root)  # Keep dialog on top
        dialog.grab_set()  # Modal

        ttk.Label(dialog, text="Time:", font=self.normal_font).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        time_entry = ttk.Entry(dialog, font=self.normal_font, width=30)
        time_entry.insert(0, original_time)
        time_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(dialog, text="Activity:", font=self.normal_font).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        activity_entry = ttk.Entry(dialog, font=self.normal_font, width=30)
        activity_entry.insert(0, original_activity)
        activity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(dialog, text="Category:", font=self.normal_font).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        category_var = tk.StringVar(value=original_category)
        category_menu = ttk.Combobox(dialog, textvariable=category_var, values=list(self.colors.keys()),
                                     font=self.normal_font, state="readonly")
        category_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        def on_save():
            new_time = time_entry.get()
            new_activity = activity_entry.get()
            new_category = category_var.get()

            if not new_time or not new_activity or not new_category:
                messagebox.showwarning("Input Error", "Time, Activity, and Category cannot be empty.", parent=dialog)
                return

            # Update internal schedule data
            self.schedule[day_key]["activities"][item_index][0] = new_time
            self.schedule[day_key]["activities"][item_index][1] = new_activity
            self.schedule[day_key]["activities"][item_index][2] = new_category

            # Update Treeview directly
            tree.item(item_iid, values=(new_time, new_activity), tags=(new_category,))
            # Re-apply color tag explicitly if needed (ttk might handle it with tag change)
            tree.tag_configure(new_category, background=self.colors.get(new_category, "#FFFFFF"))

            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=10)

        dialog.grid_columnconfigure(1, weight=1)  # Make entry fields expand

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         SAVE & LOAD FUNCTIONALITY                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def save_schedule_data(self, file_path):
        """Saves the current schedule and notes to a JSON file."""
        data_to_save = {
            "schedule": self.schedule,
            "notes": self.notes_text.get("1.0", tk.END).strip(),
            "startDate": self.date_entry.get()  # Save the start date as well
        }
        try:
            with open(file_path, "w") as f:
                json.dump(data_to_save, f, indent=4)
            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path}")
            messagebox.showinfo("Save Successful", f"Schedule saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save schedule: {e}")

    def save_schedule_dialog(self, force_dialog=False):
        if not self.current_file_path or force_dialog:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Schedule As"
            )
            if not file_path:
                return  # User cancelled
        else:
            file_path = self.current_file_path

        self.save_schedule_data(file_path)

    def load_schedule_data(self, file_path):
        """Loads schedule and notes from a JSON file."""
        try:
            with open(file_path, "r") as f:
                loaded_data = json.load(f)

            self.schedule = loaded_data.get("schedule", self._create_schedule_data())  # Fallback to default
            notes_content = loaded_data.get("notes", self.default_notes)
            start_date = loaded_data.get("startDate", datetime.date.today().strftime("%m/%d/%Y"))

            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", notes_content)

            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, start_date)

            self._populate_notebook()  # Refresh notebook with loaded data
            self.calculate_dates()  # Recalculate cycle display based on loaded date

            self.current_file_path = file_path
            self.root.title(f"Intel Technician Off‑Days Schedule - {file_path}")
            messagebox.showinfo("Load Successful", f"Schedule loaded from {file_path}")

        except FileNotFoundError:
            messagebox.showerror("Load Error", f"File not found: {file_path}")
            self._create_schedule_data()  # Load default if file not found
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", self.default_notes)
            self._populate_notebook()
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load schedule: {e}")
            self._create_schedule_data()  # Load default on other errors
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", self.default_notes)
            self._populate_notebook()

    def load_schedule_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Schedule"
        )
        if not file_path:
            return  # User cancelled
        self.load_schedule_data(file_path)

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                                CALLBACKS                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def calculate_dates(self):
        date_str = self.date_entry.get().strip()
        try:
            start_date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            messagebox.showerror("Date Error", "Please enter a valid date in MM/DD/YYYY format.")
            return
        lines = []
        for i in range(8):  # Display current 8-day cycle
            day = start_date + datetime.timedelta(days=i)
            phase = "Off" if i < 4 else "On"
            lines.append(f"{day.strftime('%A, %b %d, %Y')} – {phase} day {i % 4 + 1}")
        self.results.config(state="normal",
                            fg=self.style.lookup('TLabel', 'foreground'))  # Ensure text color matches theme
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "\n".join(lines))
        self.results.config(state="disabled")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self._set_dark_palette()
        else:
            self._set_light_palette()
        self.calculate_dates()  # Recalculate to update result box color if open

    # Removed save_notes as it's integrated into save_schedule_data
    # def save_notes(self):
    #     messagebox.showinfo("Notes", "Notes saved (not persisted in this demo).")

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           YEARLY CALENDAR (Placeholder)                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def show_yearly_calendar(self):
        # This is a placeholder. Implementation will follow.
        messagebox.showinfo("Yearly Calendar", "Yearly calendar feature coming soon!")
        #
        # TODO: Implement Yearly Calendar Window
        # - Get start date from self.date_entry
        # - Create a new Toplevel window
        # - For each month of the current year (or a selected year):
        #   - Display a calendar grid (e.g., using Labels in a Frame)
        #   - For each day in the month:
        #     - Calculate if it's an "On" or "Off" day based on the 4-on/4-off cycle.
        #     - Color-code the day or add an indicator.
        #
        # Example of how to start:
        # try:
        #     base_date_str = self.date_entry.get().strip()
        #     base_cycle_start_date = datetime.datetime.strptime(base_date_str, "%m/%d/%Y").date()
        # except ValueError:
        #     messagebox.showerror("Date Error", "Please enter a valid start date in MM/DD/YYYY format before viewing the yearly calendar.")
        #     return
        #
        # current_year = datetime.date.today().year
        # # Proceed to build calendar UI for 'current_year' using 'base_cycle_start_date'
        # # to determine the on/off status of each day.
        # # This involves calculating the number of days between base_cycle_start_date and each day
        # # in the year, then using modulo arithmetic for the 8-day cycle (4 off, 4 on).

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              THEME HELPERS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _apply_palette(self, *, bg: str, fg: str, textbg: str, treefield: str, treehead: str):
        self.root.configure(bg=bg)
        # Configure all relevant ttk widgets
        self.style.configure(".", background=bg, foreground=fg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=bg, foreground=fg)  # May need more specific styling for buttons
        self.style.configure("TFrame", background=bg)
        self.style.configure("TNotebook", background=bg)
        self.style.configure("TNotebook.Tab", background=bg, foreground=fg)  # May need specific focus/active colors
        self.style.map("TNotebook.Tab", background=[("selected", treehead)], foreground=[("selected", fg)])

        # Configure Text widgets (like notes and results)
        if hasattr(self, 'results'):  # Check if results widget exists
            self.results.configure(bg=textbg, fg=fg, insertbackground=fg, relief=tk.FLAT)
        if hasattr(self, 'notes_text'):  # Check if notes_text widget exists
            self.notes_text.configure(bg=textbg, fg=fg, insertbackground=fg)

        # Special handling for tk.Label (the main title)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label) and widget not in self.root.winfo_children()[
                0].winfo_children():  # Avoid ttk Labels
                widget.configure(bg=bg, fg=fg)
            # Apply to children of top_frame and file_ops_frame if they are standard tk widgets
            if widget.winfo_class() == 'Frame':  # like top_frame, file_ops_frame
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):  # Standard tk.Label
                        child.configure(bg=bg, fg=fg)

        self.style.configure("Treeview", background=treefield, fieldbackground=treefield, foreground=fg)
        self.style.configure("Treeview.Heading", background=treehead, foreground=fg, font=self.small_font)  # Added font
        self.style.map("Treeview", background=[("selected", "#6A9FB5")],
                       foreground=[("selected", fg if not self.dark_mode else "#FFFFFF")])
        self.style.map("Treeview.Heading", relief=[('active', 'groove'), ('pressed', 'sunken')])

        # Update legend colors to be visible on new bg
        if hasattr(self, 'legend_frames'):
            for frame, label_widget in self.legend_frames:
                # Frame color is already set from self.colors
                label_widget.configure(background=bg, foreground=fg)
        else:  # Create legend frames list if not exists (first run)
            self.legend_frames = []
            legend_container = None
            # Find legend container (assuming it's the 3rd Frame packed in root - fragile)
            # A more robust way would be to store a reference to the legend frame
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Frame):
                    # Heuristic: check if it contains labels like "Legend:"
                    is_legend = False
                    for sub_child in child.winfo_children():
                        if isinstance(sub_child, ttk.Label) and "Legend:" in sub_child.cget("text"):
                            is_legend = True
                            break
                    if is_legend:
                        legend_container = child
                        break
            if legend_container:
                for i, child in enumerate(legend_container.winfo_children()):
                    if isinstance(child, tk.Frame) and i > 0:  # tk.Frame used for color swatch
                        # Next widget should be the ttk.Label for the category name
                        if i + 1 < len(legend_container.winfo_children()) and isinstance(
                                legend_container.winfo_children()[i + 1], ttk.Label):
                            label_widget = legend_container.winfo_children()[i + 1]
                            self.legend_frames.append((child, label_widget))
                            label_widget.configure(background=bg, foreground=fg)  # Apply theme

    def _set_light_palette(self):
        self._apply_palette(bg="#f0f0f0", fg="#000000", textbg="#ffffff", treefield="#ffffff", treehead="#e1e1e1")

    def _set_dark_palette(self):
        self._apply_palette(bg="#2d2d2d", fg="#ffffff", textbg="#3a3a3a", treefield="#3a3a3a", treehead="#444444")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)  # Store the app instance
    root.mainloop()