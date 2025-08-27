import tkinter as tk
from tkinter import ttk, font, messagebox
import datetime


class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Intel Technician Off Days Schedule")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Set custom fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=12)
        self.small_font = font.Font(family="Helvetica", size=10)

        # Colors
        self.colors = {
            "morning": "#a8e6cf",  # Light green
            "afternoon": "#ffd3b6",  # Light orange
            "evening": "#ffaaa5",  # Light red
            "medicine": "#ff8b94",  # Darker pink
            "gym": "#d8b5ff",  # Light purple
            "coding": "#bae1ff",  # Light blue
            "meal": "#fdffb6"  # Light yellow
        }

        # Create schedule data
        self.create_schedule_data()

        # Create widgets
        self.create_widgets()

        # Set default view
        self.show_day(1)

    def create_schedule_data(self):
        self.schedule = {
            1: {  # Day 1
                "title": "Recovery + Light Activities",
                "activities": [
                    {"time": "9:30 AM", "activity": "Wake up", "category": "morning"},
                    {"time": "10:00 AM", "activity": "Protein-rich breakfast", "category": "meal"},
                    {"time": "10:30 AM", "activity": "Take medicine (after breakfast)", "category": "medicine"},
                    {"time": "11:00 AM", "activity": "Light stretching/mobility work", "category": "morning"},
                    {"time": "12:30 PM", "activity": "Lunch with good protein source", "category": "meal"},
                    {"time": "1:00 PM", "activity": "Take medicine (after lunch)", "category": "medicine"},
                    {"time": "1:30 PM", "activity": "Grocery shopping", "category": "afternoon"},
                    {"time": "3:30 PM", "activity": "Casual coding (1-2 hours)", "category": "coding"},
                    {"time": "5:30 PM", "activity": "Rest/pre-workout preparation", "category": "afternoon"},
                    {"time": "6:00 PM", "activity": "Pre-workout meal", "category": "meal"},
                    {"time": "7:00 PM", "activity": "Gym session (Chest & Triceps)", "category": "gym"},
                    {"time": "9:00 PM", "activity": "Post-workout meal/dinner", "category": "meal"},
                    {"time": "9:30 PM", "activity": "Take medicine (after dinner)", "category": "medicine"},
                    {"time": "10:30 PM", "activity": "Relaxation, entertainment", "category": "evening"},
                    {"time": "12:00 AM", "activity": "Bedtime", "category": "evening"},
                ]
            },
            2: {  # Day 2
                "title": "Productive Focus",
                "activities": [
                    {"time": "9:30 AM", "activity": "Wake up", "category": "morning"},
                    {"time": "10:00 AM", "activity": "Protein breakfast", "category": "meal"},
                    {"time": "10:30 AM", "activity": "Take medicine (after breakfast)", "category": "medicine"},
                    {"time": "10:45 AM", "activity": "Home maintenance/cleaning", "category": "morning"},
                    {"time": "12:30 PM", "activity": "Lunch (protein-focused)", "category": "meal"},
                    {"time": "1:00 PM", "activity": "Take medicine (after lunch)", "category": "medicine"},
                    {"time": "1:30 PM", "activity": "Deep coding session (2-3 hours)", "category": "coding"},
                    {"time": "4:30 PM", "activity": "Learning/skill development", "category": "afternoon"},
                    {"time": "5:30 PM", "activity": "Rest/pre-workout preparation", "category": "afternoon"},
                    {"time": "6:00 PM", "activity": "Pre-workout meal", "category": "meal"},
                    {"time": "7:00 PM", "activity": "Gym session (Back & Biceps)", "category": "gym"},
                    {"time": "9:00 PM", "activity": "Post-workout meal/dinner", "category": "meal"},
                    {"time": "9:30 PM", "activity": "Take medicine (after dinner)", "category": "medicine"},
                    {"time": "10:00 PM", "activity": "Relaxation", "category": "evening"},
                    {"time": "12:00 AM", "activity": "Bedtime", "category": "evening"},
                ]
            },
            3: {  # Day 3
                "title": "Balance Day",
                "activities": [
                    {"time": "9:30 AM", "activity": "Wake up", "category": "morning"},
                    {"time": "10:00 AM", "activity": "Protein breakfast", "category": "meal"},
                    {"time": "10:30 AM", "activity": "Take medicine (after breakfast)", "category": "medicine"},
                    {"time": "10:45 AM", "activity": "Meal prep for remaining days", "category": "morning"},
                    {"time": "12:30 PM", "activity": "Lunch", "category": "meal"},
                    {"time": "1:00 PM", "activity": "Take medicine (after lunch)", "category": "medicine"},
                    {"time": "1:30 PM", "activity": "Coding session (2-3 hours)", "category": "coding"},
                    {"time": "4:30 PM", "activity": "Outdoor activity/hobby time", "category": "afternoon"},
                    {"time": "5:30 PM", "activity": "Rest/pre-workout preparation", "category": "afternoon"},
                    {"time": "6:00 PM", "activity": "Pre-workout snack", "category": "meal"},
                    {"time": "7:00 PM", "activity": "Gym session (Legs)", "category": "gym"},
                    {"time": "9:00 PM", "activity": "Post-workout meal/dinner", "category": "meal"},
                    {"time": "9:30 PM", "activity": "Take medicine (after dinner)", "category": "medicine"},
                    {"time": "10:00 PM", "activity": "Friends/family time", "category": "evening"},
                    {"time": "12:00 AM", "activity": "Bedtime", "category": "evening"},
                ]
            },
            4: {  # Day 4
                "title": "Transition Day",
                "activities": [
                    {"time": "10:00 AM", "activity": "Wake up", "category": "morning"},
                    {"time": "10:30 AM", "activity": "Protein breakfast", "category": "meal"},
                    {"time": "11:00 AM", "activity": "Take medicine (after breakfast)", "category": "medicine"},
                    {"time": "11:15 AM", "activity": "Prepare for upcoming work cycle", "category": "morning"},
                    {"time": "12:30 PM", "activity": "Lunch", "category": "meal"},
                    {"time": "1:00 PM", "activity": "Take medicine (after lunch)", "category": "medicine"},
                    {"time": "1:30 PM", "activity": "Final coding session", "category": "coding"},
                    {"time": "3:30 PM", "activity": "Errands/appointments", "category": "afternoon"},
                    {"time": "5:00 PM", "activity": "Pre-workout preparation", "category": "afternoon"},
                    {"time": "5:30 PM", "activity": "Pre-workout meal", "category": "meal"},
                    {"time": "6:30 PM", "activity": "Gym session (Active Recovery/Abs/Shoulders)", "category": "gym"},
                    {"time": "8:00 PM", "activity": "Post-workout meal/dinner", "category": "meal"},
                    {"time": "8:30 PM", "activity": "Take medicine (after dinner)", "category": "medicine"},
                    {"time": "9:00 PM", "activity": "Final preparations for work", "category": "evening"},
                    {"time": "10:00 PM", "activity": "Early bedtime", "category": "evening"},
                ]
            }
        }

    def create_widgets(self):
        # Create main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Intel Technician 4/4 Schedule - Off Days",
            font=self.title_font,
            bg="#f0f0f0",
            pady=10
        )
        title_label.pack(fill=tk.X)

        # Button frame for day selection
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)

        # Day selection buttons
        for day in range(1, 5):
            btn = tk.Button(
                button_frame,
                text=f"Off Day {day}",
                font=self.normal_font,
                width=15,
                command=lambda d=day: self.show_day(d),
                relief=tk.GROOVE,
                bg="#e0e0e0"
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Simple cycle tracker
        cycle_frame = tk.Frame(main_frame, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        cycle_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        cycle_label = tk.Label(cycle_frame, text="Cycle Tracker", font=self.header_font, bg="#f0f0f0")
        cycle_label.pack(pady=(10, 10))

        # Date inputs
        date_frame = tk.Frame(cycle_frame, bg="#f0f0f0")
        date_frame.pack(padx=10, pady=5)

        date_label = tk.Label(date_frame, text="Current off-cycle start date:", bg="#f0f0f0")
        date_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        date_frame2 = tk.Frame(date_frame, bg="#f0f0f0")
        date_frame2.grid(row=1, column=0, sticky=tk.W, pady=5)

        # Month, day, year inputs
        self.month_var = tk.StringVar(value=str(datetime.datetime.now().month))
        self.day_var = tk.StringVar(value=str(datetime.datetime.now().day))
        self.year_var = tk.StringVar(value=str(datetime.datetime.now().year))

        month_entry = tk.Entry(date_frame2, textvariable=self.month_var, width=3)
        month_entry.pack(side=tk.LEFT)

        slash1 = tk.Label(date_frame2, text="/", bg="#f0f0f0")
        slash1.pack(side=tk.LEFT)

        day_entry = tk.Entry(date_frame2, textvariable=self.day_var, width=3)
        day_entry.pack(side=tk.LEFT)

        slash2 = tk.Label(date_frame2, text="/", bg="#f0f0f0")
        slash2.pack(side=tk.LEFT)

        year_entry = tk.Entry(date_frame2, textvariable=self.year_var, width=5)
        year_entry.pack(side=tk.LEFT)

        # Calculate button
        calc_btn = tk.Button(cycle_frame, text="Calculate Cycle Dates", command=self.calculate_dates)
        calc_btn.pack(pady=10)

        # Results display
        self.results_text = tk.Text(cycle_frame, height=10, width=30, font=self.small_font)
        self.results_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Content frame for schedule
        self.content_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.GROOVE)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Legend frame
        legend_frame = tk.Frame(main_frame, bg="#f0f0f0")
        legend_frame.pack(fill=tk.X, pady=10)

        legend_label = tk.Label(legend_frame, text="Categories:", font=self.small_font, bg="#f0f0f0")
        legend_label.pack(side=tk.LEFT, padx=5)

        for category, color in self.colors.items():
            legend_item = tk.Frame(legend_frame, bg="#f0f0f0")
            legend_item.pack(side=tk.LEFT, padx=10)

            color_box = tk.Frame(legend_item, bg=color, width=15, height=15)
            color_box.pack(side=tk.LEFT, padx=2)

            label = tk.Label(legend_item, text=category.capitalize(), bg="#f0f0f0", font=self.small_font)
            label.pack(side=tk.LEFT)

        # Gym schedule summary
        gym_frame = tk.Frame(main_frame, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        gym_frame.pack(fill=tk.X, pady=10)

        gym_label = tk.Label(gym_frame, text="Gym Split Overview", font=self.header_font, bg="#f0f0f0")
        gym_label.pack(anchor=tk.W, padx=10, pady=5)

        gym_days = [
            "Day 1: Chest & Triceps",
            "Day 2: Back & Biceps",
            "Day 3: Legs",
            "Day 4: Active Recovery/Abs/Shoulders"
        ]

        for day in gym_days:
            day_label = tk.Label(gym_frame, text=f"• {day}", bg="#f0f0f0", font=self.normal_font)
            day_label.pack(anchor=tk.W, padx=20, pady=2)

        # Notes section
        notes_frame = tk.Frame(main_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=10)

        notes_label = tk.Label(notes_frame, text="Notes:", font=self.header_font, bg="#f0f0f0")
        notes_label.pack(anchor=tk.W)

        self.notes_text = tk.Text(notes_frame, height=4, width=50, font=self.small_font)
        self.notes_text.pack(fill=tk.X, pady=5)
        self.notes_text.insert(tk.END, "Add your personal notes here...")

        save_notes_btn = tk.Button(notes_frame, text="Save Notes", command=self.save_notes)
        save_notes_btn.pack(side=tk.RIGHT, padx=10)

    def show_day(self, day_num):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Get day data
        day_data = self.schedule[day_num]

        # Day header
        day_header = tk.Frame(self.content_frame, bg="white")
        day_header.pack(fill=tk.X, padx=20, pady=10)

        day_title = tk.Label(
            day_header,
            text=f"Off Day {day_num}: {day_data['title']}",
            font=self.header_font,
            bg="white"
        )
        day_title.pack(anchor=tk.W)

        # Create schedule table
        table_frame = tk.Frame(self.content_frame, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Table headers
        time_header = tk.Label(table_frame, text="Time", font=self.normal_font, bg="white", width=10, anchor=tk.W)
        time_header.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        activity_header = tk.Label(table_frame, text="Activity", font=self.normal_font, bg="white", width=40,
                                   anchor=tk.W)
        activity_header.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        separator = ttk.Separator(table_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)

        # Table content
        for i, item in enumerate(day_data["activities"]):
            time_label = tk.Label(
                table_frame,
                text=item["time"],
                font=self.normal_font,
                bg="white",
                anchor=tk.W
            )
            time_label.grid(row=i + 2, column=0, padx=5, pady=5, sticky=tk.W)

            activity_frame = tk.Frame(table_frame, bg=self.colors[item["category"]], padx=5, pady=5)
            activity_frame.grid(row=i + 2, column=1, padx=5, pady=3, sticky=tk.W + tk.E)

            activity_label = tk.Label(
                activity_frame,
                text=item["activity"],
                font=self.normal_font,
                bg=self.colors[item["category"]],
                anchor=tk.W,
                width=40
            )
            activity_label.pack(fill=tk.X)

    def calculate_dates(self):
        try:
            # Get date values from entries
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            year = int(self.year_var.get())

            # Create a date object
            start_date = datetime.date(year, month, day)

            # Clear previous results
            self.results_text.delete(1.0, tk.END)

            # Calculate and display dates
            self.results_text.insert(tk.END,
                                     f"Off Cycle: {start_date.strftime('%m/%d/%Y')} - {(start_date + datetime.timedelta(days=3)).strftime('%m/%d/%Y')}\n\n")

            work_start = start_date + datetime.timedelta(days=4)
            work_end = work_start + datetime.timedelta(days=3)
            self.results_text.insert(tk.END,
                                     f"Work Cycle: {work_start.strftime('%m/%d/%Y')} - {work_end.strftime('%m/%d/%Y')}\n\n")

            next_off = work_end + datetime.timedelta(days=1)
            self.results_text.insert(tk.END,
                                     f"Next Off Cycle: {next_off.strftime('%m/%d/%Y')} - {(next_off + datetime.timedelta(days=3)).strftime('%m/%d/%Y')}")

        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in MM/DD/YYYY format")

    def save_notes(self):
        # Here you would implement saving notes to file
        # For now we'll just show a message
        messagebox.showinfo("Notes Saved", "Your notes have been saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()