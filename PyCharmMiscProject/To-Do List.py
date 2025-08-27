import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive To-Do List")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Initialize data
        self.tasks = []
        self.filename = "tasks.json"
        self.load_tasks()

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f5f5f5")
        self.style.configure("Task.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        self.style.configure("Task.TLabel", background="#ffffff")
        self.style.configure("Completed.Task.TFrame", background="#e8f5e9")
        self.style.configure("Completed.Task.TLabel", background="#e8f5e9", foreground="#757575")

        # Create header
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="My To-Do List", style="Header.TLabel").pack(side=tk.LEFT)

        # Create buttons frame
        buttons_frame = ttk.Frame(header_frame, style="TFrame")
        buttons_frame.pack(side=tk.RIGHT)

        ttk.Button(buttons_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        # Create search frame
        search_frame = ttk.Frame(self.main_frame, style="TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_tasks())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create filter frame
        filter_frame = ttk.Frame(self.main_frame, style="TFrame")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, value="all",
                        command=self.filter_tasks).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(filter_frame, text="Active", variable=self.filter_var, value="active",
                        command=self.filter_tasks).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(filter_frame, text="Completed", variable=self.filter_var, value="completed",
                        command=self.filter_tasks).pack(side=tk.LEFT)

        # Create canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame, background="#f5f5f5", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)

        self.tasks_frame = ttk.Frame(self.canvas, style="TFrame")
        self.tasks_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Display tasks
        self.update_task_display()
        self.update_status()

        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda event: self.add_task())
        self.root.bind("<Delete>", lambda event: self.delete_selected())

    def load_tasks(self):
        """Load tasks from JSON file if it exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    self.tasks = json.load(file)
            except json.JSONDecodeError:
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.filename, "w") as file:
            json.dump(self.tasks, file, indent=4)

    def add_task(self):
        """Add a new task"""
        title = simpledialog.askstring("Add Task", "Enter task title:")
        if title:
            description = simpledialog.askstring("Add Task", "Enter task description (optional):")

            task = {
                "id": len(self.tasks) + 1,
                "title": title,
                "description": description or "",
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "selected": False
            }

            self.tasks.append(task)
            self.save_tasks()
            self.update_task_display()
            self.update_status()

    def toggle_task_completion(self, task_id):
        """Toggle task completion status"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                self.save_tasks()
                self.update_task_display()
                self.update_status()
                break

    def toggle_task_selection(self, task_id):
        """Toggle task selection status"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["selected"] = not task.get("selected", False)
                self.update_task_display()
                break

    def delete_selected(self):
        """Delete selected tasks"""
        selected_tasks = [task for task in self.tasks if task.get("selected", False)]

        if not selected_tasks:
            messagebox.showinfo("No Selection", "No tasks selected. Please select tasks to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete {len(selected_tasks)} selected task(s)?")
        if confirm:
            self.tasks = [task for task in self.tasks if not task.get("selected", False)]
            # Reassign IDs to maintain sequence
            for i, task in enumerate(self.tasks):
                task["id"] = i + 1
            self.save_tasks()
            self.update_task_display()
            self.update_status()

    def show_task_details(self, task_id):
        """Show details of a specific task"""
        for task in self.tasks:
            if task["id"] == task_id:
                details = f"Created: {task['created_at']}\n\n"
                details += f"Description: {task['description'] if task['description'] else 'No description'}"
                messagebox.showinfo(f"Task Details: {task['title']}", details)
                break

    def filter_tasks(self):
        """Filter tasks based on search and filter criteria"""
        self.update_task_display()

    def update_task_display(self):
        """Update the task display"""
        # Clear existing tasks
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        # Filter tasks
        search_term = self.search_var.get().lower()
        filter_option = self.filter_var.get()

        filtered_tasks = []
        for task in self.tasks:
            # Apply search filter
            if search_term and search_term not in task["title"].lower():
                continue

            # Apply status filter
            if filter_option == "active" and task["completed"]:
                continue
            if filter_option == "completed" and not task["completed"]:
                continue

            filtered_tasks.append(task)

        # Display filtered tasks
        for i, task in enumerate(filtered_tasks):
            task_style = "Completed.Task.TFrame" if task["completed"] else "Task.TFrame"
            label_style = "Completed.Task.TLabel" if task["completed"] else "Task.TLabel"

            task_frame = ttk.Frame(self.tasks_frame, style=task_style)
            task_frame.pack(fill=tk.X, pady=5)

            # Selection checkbox
            selected_var = tk.BooleanVar(value=task.get("selected", False))
            cb = ttk.Checkbutton(task_frame, variable=selected_var,
                                 command=lambda t=task["id"]: self.toggle_task_selection(t))
            cb.pack(side=tk.LEFT, padx=5)

            # Completion checkbox
            completed_var = tk.BooleanVar(value=task["completed"])
            cb = ttk.Checkbutton(task_frame, variable=completed_var,
                                 command=lambda t=task["id"]: self.toggle_task_completion(t))
            cb.pack(side=tk.LEFT, padx=5)

            # Task title
            title_label = ttk.Label(task_frame, text=task["title"], style=label_style)
            title_label.pack(side=tk.LEFT, padx=5)

            # Button to show details
            details_btn = ttk.Button(task_frame, text="Details",
                                     command=lambda t=task["id"]: self.show_task_details(t))
            details_btn.pack(side=tk.RIGHT, padx=5)

    def update_status(self):
        """Update the status bar"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        self.status_var.set(f"Total tasks: {total} | Completed: {completed} | Remaining: {total - completed}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()