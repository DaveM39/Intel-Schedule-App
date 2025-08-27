import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime
import pandas as pd


class INRMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("INR Monitoring Application")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Initialize database
        self.init_database()

        # Create UI
        self.create_ui()

        # Load existing data
        self.load_data()

    def init_database(self):
        # Connect to sqlite database (will create if doesn't exist)
        self.conn = sqlite3.connect('inr_data.db')
        self.cursor = self.conn.cursor()

        # Create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inr_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                inr_value REAL NOT NULL,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def create_ui(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.input_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        self.graph_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.input_frame, text="Record INR")
        self.notebook.add(self.history_frame, text="History")
        self.notebook.add(self.graph_frame, text="Graph")

        # Setup each tab
        self.setup_input_tab()
        self.setup_history_tab()
        self.setup_graph_tab()

    def setup_input_tab(self):
        # Date field
        date_frame = ttk.Frame(self.input_frame)
        date_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT)

        self.date_entry = ttk.Entry(date_frame)
        self.date_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # INR value field
        inr_frame = ttk.Frame(self.input_frame)
        inr_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(inr_frame, text="INR Value:").pack(side=tk.LEFT)

        self.inr_entry = ttk.Entry(inr_frame)
        self.inr_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Notes field
        notes_frame = ttk.Frame(self.input_frame)
        notes_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        ttk.Label(notes_frame, text="Notes:").pack(anchor=tk.W)

        self.notes_text = tk.Text(notes_frame, height=5)
        self.notes_text.pack(fill=tk.BOTH, pady=5, expand=True)

        # Submit button
        submit_btn = ttk.Button(self.input_frame, text="Save Reading", command=self.save_reading)
        submit_btn.pack(pady=20)

    def setup_history_tab(self):
        # Create treeview for data display
        columns = ("Date", "INR Value", "Notes")
        self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")

        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.column("Notes", width=300)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Button frame
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Delete button
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_reading)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Export button
        export_btn = ttk.Button(btn_frame, text="Export Data", command=self.export_data)
        export_btn.pack(side=tk.LEFT, padx=5)

    def setup_graph_tab(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control frame for date range
        control_frame = ttk.Frame(self.graph_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Show last:").pack(side=tk.LEFT)

        self.time_var = tk.StringVar(value="all")
        time_options = ["all", "1 month", "3 months", "6 months", "1 year"]

        time_dropdown = ttk.Combobox(control_frame, textvariable=self.time_var, values=time_options)
        time_dropdown.pack(side=tk.LEFT, padx=5)

        update_btn = ttk.Button(control_frame, text="Update Graph", command=self.update_graph)
        update_btn.pack(side=tk.LEFT, padx=5)

    def save_reading(self):
        # Get values from inputs
        date = self.date_entry.get()

        try:
            inr_value = float(self.inr_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "INR value must be a number.")
            return

        notes = self.notes_text.get("1.0", tk.END).strip()

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
            return

        # Save to database
        self.cursor.execute(
            "INSERT INTO inr_readings (date, inr_value, notes) VALUES (?, ?, ?)",
            (date, inr_value, notes)
        )
        self.conn.commit()

        # Show alert based on INR value
        self.check_inr_alert(inr_value)

        # Clear form
        self.inr_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Reload data
        self.load_data()

        # Switch to graph tab
        self.notebook.select(self.graph_frame)

    def check_inr_alert(self, inr_value):
        if inr_value < 2.0:
            messagebox.showwarning("Low INR",
                                   f"Your INR value ({inr_value}) is below the therapeutic range (2.0-3.0). Consider consulting your healthcare provider.")
        elif inr_value > 3.0:
            messagebox.showwarning("High INR",
                                   f"Your INR value ({inr_value}) is above the therapeutic range (2.0-3.0). Consider consulting your healthcare provider.")
        else:
            messagebox.showinfo("Normal INR",
                                f"Your INR value ({inr_value}) is within the therapeutic range (2.0-3.0).")

    def load_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get data from database
        self.cursor.execute("SELECT date, inr_value, notes FROM inr_readings ORDER BY date DESC")
        rows = self.cursor.fetchall()

        # Populate treeview
        for row in rows:
            self.tree.insert("", "end", values=row)

        # Update graph
        self.update_graph()

    def delete_reading(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a record to delete.")
            return

        # Get values of selected item
        values = self.tree.item(selected_item[0], "values")

        # Delete from database
        self.cursor.execute(
            "DELETE FROM inr_readings WHERE date = ? AND inr_value = ?",
            (values[0], values[1])
        )
        self.conn.commit()

        # Reload data
        self.load_data()

    def export_data(self):
        # Get data from database
        self.cursor.execute("SELECT date, inr_value, notes FROM inr_readings ORDER BY date")
        rows = self.cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=["Date", "INR Value", "Notes"])

        try:
            # Export to CSV
            filename = "inr_data_export.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting data: {str(e)}")

    def update_graph(self):
        # Clear figure
        self.ax.clear()

        # Get data from database
        self.cursor.execute("SELECT date, inr_value FROM inr_readings ORDER BY date")
        rows = self.cursor.fetchall()

        if not rows:
            self.ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            self.canvas.draw()
            return

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=["date", "inr_value"])
        df["date"] = pd.to_datetime(df["date"])

        # Filter based on selected time range
        time_range = self.time_var.get()
        if time_range != "all":
            months = {"1 month": 1, "3 months": 3, "6 months": 6, "1 year": 12}
            if time_range in months:
                cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months[time_range])
                df = df[df["date"] > cutoff_date]

        # Create plot
        self.ax.plot(df["date"], df["inr_value"], 'b-o')

        # Add reference lines for therapeutic range
        self.ax.axhline(y=2.0, color='g', linestyle='--', alpha=0.7)
        self.ax.axhline(y=3.0, color='r', linestyle='--', alpha=0.7)

        # Fill therapeutic range area
        self.ax.fill_between(df["date"], 2.0, 3.0, color='g', alpha=0.1)

        # Customize plot
        self.ax.set_title("INR Values Over Time")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("INR Value")
        self.ax.grid(True, alpha=0.3)

        # Set y-axis limits with some padding
        max_inr = max(df["inr_value"].max(), 3.0) + 0.5
        min_inr = min(df["inr_value"].min(), 2.0) - 0.5
        self.ax.set_ylim(min_inr, max_inr)

        # Add text annotations for therapeutic range
        x_pos = df["date"].min()
        self.ax.text(x_pos, 3.1, "Upper Limit (3.0)", color='r', fontsize=8)
        self.ax.text(x_pos, 1.9, "Lower Limit (2.0)", color='g', fontsize=8)

        # Format x-axis dates
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Draw canvas
        self.canvas.draw()

    def __del__(self):
        # Close database connection
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    root = tk.Tk()
    app = INRMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()