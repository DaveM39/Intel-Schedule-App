import tkinter as tk
from tkinter import ttk, font, messagebox
import datetime


class ScheduleApp:
    """A modern 4‑on / 4‑off planner tailored for Intel technicians.

    Features
    --------
    ▸ Notebook tabs – each off‑day on its own tab with colour‑coded Treeview rows.
    ▸ Cycle calculator – enter the first off‑day date and get the next 8‑day block mapped.
    ▸ Dark‑mode toggle – instant light/dark switch.
    ▸ Personal notes – quick scratch‑pad area.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Intel Technician Off‑Days Schedule")
        self.root.geometry("1000x700")
        self.dark_mode = False

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
        self._create_schedule_data()
        self._populate_notebook()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               UI BUILDERS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _build_widgets(self):
        tk.Label(self.root, text="Intel Technician • 4‑On / 4‑Off Planner", font=self.title_font)\
            .pack(pady=(15, 5))

        # Top toolbar
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=20)
        ttk.Label(top, text="Current off‑cycle start date (MM/DD/YYYY):")\
            .pack(side=tk.LEFT, padx=(0, 8))
        self.date_entry = ttk.Entry(top, width=12, font=self.normal_font)
        self.date_entry.insert(0, datetime.date.today().strftime("%m/%d/%Y"))
        self.date_entry.pack(side=tk.LEFT)
        ttk.Button(top, text="Calculate Cycle", command=self.calculate_dates).pack(side=tk.LEFT, padx=10)
        ttk.Button(top, text="Toggle Dark Mode", command=self.toggle_theme).pack(side=tk.RIGHT)

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
        notes = ttk.Frame(self.root)
        notes.pack(fill=tk.BOTH, padx=20, pady=(0, 10))
        ttk.Label(notes, text="Personal Notes:", font=self.header_font).pack(anchor=tk.W, pady=(0, 4))
        self.notes_text = tk.Text(notes, height=4, font=self.small_font)
        self.notes_text.pack(fill=tk.BOTH)
        ttk.Button(notes, text="Save Notes", command=self.save_notes).pack(anchor=tk.E, pady=4)

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                       DATA & NOTEBOOK POPULATION                         ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _create_schedule_data(self):
        """Hard‑coded demo agenda for the 4 off‑days. Day‑1 now begins with post‑night‑shift sleep."""

        self.schedule = {
            1: {
                "title": "Recovery after Night Shift",
                "activities": [
                    ("10:00 AM", "Sleep (post‑shift, until ≈3:30 PM)", "sleep"),
                    ("3:30 PM", "Wake up", "morning"),
                    ("4:00 PM", "Protein‑rich meal", "meal"),
                    ("4:30 PM", "Take medicine (after meal)", "medicine"),
                    ("5:00 PM", "Light stretching / mobility", "morning"),
                    ("5:30 PM", "Grocery shopping", "afternoon"),
                    ("7:00 PM", "Pre‑workout snack", "meal"),
                    ("8:00 PM", "Gym – Chest & Triceps", "gym"),
                    ("10:00 PM", "Post‑workout meal", "meal"),
                    ("10:30 PM", "Take medicine (after meal)", "medicine"),
                    ("11:00 PM", "Relaxation", "evening"),
                    ("12:30 AM", "Bedtime", "evening"),
                ],
            },
            2: {
                "title": "Productive Focus",
                "activities": [
                    ("9:30 AM", "Wake up", "morning"),
                    ("10:00 AM", "Protein breakfast", "meal"),
                    ("10:30 AM", "Take medicine (after breakfast)", "medicine"),
                    ("10:45 AM", "Home maintenance / cleaning", "morning"),
                    ("12:30 PM", "Lunch", "meal"),
                    ("1:00 PM", "Take medicine (after lunch)", "medicine"),
                    ("1:30 PM", "Deep coding session (2–3 h)", "coding"),
                    ("4:30 PM", "Learning – online course", "afternoon"),
                    ("5:30 PM", "Rest / pre‑workout prep", "afternoon"),
                    ("6:00 PM", "Pre‑workout meal", "meal"),
                    ("7:00 PM", "Gym – Back & Biceps", "gym"),
                    ("9:00 PM", "Post‑workout dinner", "meal"),
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
                    ("1:30 PM", "Coding session (2–3 h)", "coding"),
                    ("4:30 PM", "Outdoor hobby / walk", "afternoon"),
                    ("5:30 PM", "Rest / pre‑workout prep", "afternoon"),
                    ("6:00 PM", "Pre‑workout snack", "meal"),
                    ("7:00 PM", "Gym – Shoulders & Abs", "gym"),
                    ("9:00 PM", "Post‑workout dinner", "meal"),
                    ("9:30 PM", "Take medicine (after dinner)", "medicine"),
                    ("10:00 PM", "Reading / downtime", "evening"),
                    ("12:00 AM", "Bedtime", "evening"),
                ],
            },
            4: {
                "title": "Social / Rest",
                "activities": [
                    ("9:30 AM", "Wake up", "morning"),
                    ("10:00 AM", "Easy breakfast", "meal"),
                    ("10:30 AM", "Take medicine (after breakfast)", "medicine"),
                    ("11:00 AM", "Laundry & chores", "morning"),
                    ("12:30 PM", "Lunch – meet a friend", "meal"),
                    ("1:30 PM", "Free time / errands", "afternoon"),
                    ("4:30 PM", "Prep for upcoming work block", "afternoon"),
                    ("6:00 PM", "Light gym – Stretch & Cardio", "gym"),
                    ("7:30 PM", "Cheat‑meal dinner out", "meal"),
                    ("9:00 PM", "Relax with family / friends", "evening"),
                    ("11:00 PM", "Early bedtime", "evening"),
                ],
            },
        }

    def _populate_notebook(self):
        for day, info in self.schedule.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Day {day}")
            ttk.Label(tab, text=info["title"], font=self.header_font).pack(anchor=tk.W, pady=(6, 4), padx=6)

            tree = ttk.Treeview(tab, columns=("time", "activity"), show="headings", height=14)
            tree.heading("time", text="Time")
            tree.heading("activity", text="Activity")
            tree.column("time", width=90, anchor=tk.CENTER)
            tree.column("activity", width=700)
            for cat, col in self.colors.items():
                tree.tag_configure(cat, background=col)
            for t, act, cat in info["activities"]:
                tree.insert("", tk.END, values=(t, act), tags=(cat,))
            vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
            tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 10))

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
        for i in range(8):
            day = start_date + datetime.timedelta(days=i)
            phase = "Off" if i < 4 else "On"
            lines.append(f"{day.strftime('%A, %b %d, %Y')} – {phase} day {i % 4 + 1}")
        self.results.config(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "\n".join(lines))
        self.results.config(state="disabled")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self._set_dark_palette()
        else:
            self._set_light_palette()

    def save_notes(self):
        messagebox.showinfo("Notes", "Notes saved (not persisted in this demo).")

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              THEME HELPERS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    def _set_light_palette(self):
        self._apply_palette(bg="#f0f0f0", fg="#000000", textbg="#ffffff", treefield="#ffffff", treehead="#e1e1e1")

    def _set_dark_palette(self):
        self._apply_palette(bg="#2d2d2d", fg="#ffffff", textbg="#3a3a3a", treefield="#3a3a3a", treehead="#444444")

    def _apply_palette(self, *, bg: str, fg: str, textbg: str, treefield: str, treehead: str):
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(bg=textbg, fg=fg, insertbackground=fg)
        self.style.configure("Treeview", background=treefield, fieldbackground=treefield, foreground=fg)
        self.style.configure("Treeview.Heading", background=treehead, foreground=fg)
        self.style.map("Treeview", background=[("selected", "#6A9FB5")])


if __name__ == "__main__":
    root = tk.Tk()
    ScheduleApp(root)
    root.mainloop()
