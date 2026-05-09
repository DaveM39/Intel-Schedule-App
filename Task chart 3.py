from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
import argparse
import sys

OUTPUT_FILE = Path("task_chart.md")
STATUS_NOT_DONE = "☐ Not done"
STATUS_DONE = "☑ Done"


@dataclass
class Task:
    name: str
    priority: str
    done: bool = False

    @property
    def status(self) -> str:
        return STATUS_DONE if self.done else STATUS_NOT_DONE


TASKS: OrderedDict[str, list[Task]] = OrderedDict(
    {
        "Short-Term": [
            Task("Clean and organize room/work area", "Medium"),
            Task("Buy groceries", "High"),
            Task("Buy supplements/medicine", "High"),
            Task("Do laundry", "Medium"),
            Task("Pay bills", "High"),
            Task("Check bank/credit card charges", "Medium"),
            Task("Schedule gym sessions", "Medium"),
            Task("Prepare meals for the next few days", "Medium"),
            Task("Buy new clothes for gym or social events", "Medium"),
            Task("Buy new shirts for work", "Medium"),
            Task("Buy cleaning spray for glasses", "Low"),
        ],
        "Long-Term": [
            Task("Save money every month", "High"),
            Task("Work on career/job progress", "High"),
            Task("Improve English/Chinese/programming skills", "Medium"),
            Task("Build or improve personal app/project", "Medium"),
            Task("Get a driver's license", "High"),
            Task("Plan future travel", "Low"),
            Task("Find rental housing — Ashkelon/other city", "High"),
        ],
        "House Renovation": [
            Task("Fill gaps/holes between floor tiles", "High"),
            Task("Seal shower with silicone", "High"),
            Task("Paint walls", "Medium"),
            Task("Check bathroom water leaks", "High"),
            Task("Buy renovation supplies", "High"),
        ],
    }
)


def build_markdown(tasks_by_category: OrderedDict[str, list[Task]]) -> str:
    lines = [
        "# Task Chart",
        "",
        "| Category | Task | Priority | Status |",
        "|---|---|---|---|",
    ]

    for category, tasks in tasks_by_category.items():
        for task in tasks:
            lines.append(f"| **{category}** | {task.name} | {task.priority} | {task.status} |")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| Category | Number of Tasks |",
            "|---|---:|",
        ]
    )

    for category, tasks in tasks_by_category.items():
        lines.append(f"| **{category}** | {len(tasks)} |")

    return "\n".join(lines) + "\n"


def export_markdown(tasks_by_category: OrderedDict[str, list[Task]]) -> Path:
    OUTPUT_FILE.write_text(build_markdown(tasks_by_category), encoding="utf-8")
    return OUTPUT_FILE.resolve()


def run_desktop_app() -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ModuleNotFoundError:
        print("Tkinter is not installed for this Python environment.")
        print("Install it on Ubuntu with:")
        print("  sudo apt-get update")
        print("  sudo apt-get install -y python3-tk")
        return 1

    class TaskChartDesktopApp(tk.Tk):
        def __init__(self, tk_module, ttk_module, msg_module) -> None:
            super().__init__()
            # Renamed these so they don't overwrite internal tkinter attributes
            self.tk_mod = tk_module
            self.ttk_mod = ttk_module
            self.msg_mod = msg_module

            self.title("Task Chart")
            self.geometry("1020x700")
            self.minsize(860, 560)
            self.configure(bg="#f5f7fb")

            self.task_vars: OrderedDict[str, list[tuple[Task, tk.BooleanVar, ttk.Label, ttk.Label]]] = OrderedDict()

            self._configure_styles()
            self._build_layout()
            self._build_task_tabs()
            self._update_summary()

        def _configure_styles(self) -> None:
            style = self.ttk_mod.Style(self)
            style.theme_use("clam")

            style.configure("Root.TFrame", background="#f5f7fb")
            style.configure("Card.TFrame", background="#ffffff")
            style.configure("Title.TLabel", background="#f5f7fb", foreground="#172033", font=("Arial", 24, "bold"))
            style.configure("Subtitle.TLabel", background="#f5f7fb", foreground="#667085", font=("Arial", 10))
            style.configure("CardTitle.TLabel", background="#ffffff", foreground="#172033", font=("Arial", 13, "bold"))
            style.configure("Header.TLabel", background="#e9edf5", foreground="#344054", font=("Arial", 10, "bold"))

            style.configure("Task.TLabel", background="#ffffff", foreground="#172033", font=("Arial", 10))
            style.configure("DoneTask.TLabel", background="#ffffff", foreground="#98a2b3",
                            font=("Arial", 10, "overstrike"))

            style.configure("Status.TLabel", background="#ffffff", foreground="#667085", font=("Arial", 10))
            style.configure("High.TLabel", background="#fee2e2", foreground="#991b1b", font=("Arial", 9, "bold"))
            style.configure("Medium.TLabel", background="#fef3c7", foreground="#92400e", font=("Arial", 9, "bold"))
            style.configure("Low.TLabel", background="#dcfce7", foreground="#166534", font=("Arial", 9, "bold"))

            style.configure("Primary.TButton", font=("Arial", 10, "bold"), padding=(14, 8))
            style.configure("Secondary.TButton", font=("Arial", 10), padding=(14, 8))
            style.configure("Danger.TButton", font=("Arial", 9), foreground="#991b1b", padding=(8, 4))

            style.configure("TNotebook", background="#f5f7fb", borderwidth=0)
            style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=(16, 8))

        def _build_layout(self) -> None:
            self.columnconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            header = self.ttk_mod.Frame(self, style="Root.TFrame", padding=(24, 20, 24, 12))
            header.grid(row=0, column=0, sticky="ew")
            header.columnconfigure(0, weight=1)

            self.ttk_mod.Label(header, text="Task Chart", style="Title.TLabel").grid(row=0, column=0, sticky="w")
            self.ttk_mod.Label(
                header,
                text="A desktop task chart for short-term plans, long-term goals, and house renovation.",
                style="Subtitle.TLabel",
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

            actions = self.ttk_mod.Frame(header, style="Root.TFrame")
            actions.grid(row=0, column=1, rowspan=2, sticky="e")

            self.ttk_mod.Button(
                actions,
                text="+ Add Task",
                style="Primary.TButton",
                command=self._open_add_task_dialog,
            ).grid(row=0, column=0, padx=(0, 8))

            self.ttk_mod.Button(
                actions,
                text="Export Markdown",
                style="Secondary.TButton",
                command=self._export_markdown,
            ).grid(row=0, column=1, padx=(0, 8))

            self.ttk_mod.Button(
                actions,
                text="Reset Status",
                style="Secondary.TButton",
                command=self._reset_statuses,
            ).grid(row=0, column=2)

            body = self.ttk_mod.Frame(self, style="Root.TFrame", padding=(24, 0, 24, 24))
            body.grid(row=1, column=0, sticky="nsew")
            body.columnconfigure(0, weight=1)
            body.columnconfigure(1, weight=0)
            body.rowconfigure(0, weight=1)

            self.notebook = self.ttk_mod.Notebook(body)
            self.notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

            summary_card = self.ttk_mod.Frame(body, style="Card.TFrame", padding=18)
            summary_card.grid(row=0, column=1, sticky="ns")
            summary_card.columnconfigure(0, weight=1)

            self.ttk_mod.Label(summary_card, text="Summary", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
            self.summary_text = self.tk_mod.Text(
                summary_card,
                width=30,
                height=16,
                bg="#ffffff",
                fg="#172033",
                bd=0,
                highlightthickness=0,
                font=("Arial", 10),
                state="disabled",
            )
            self.summary_text.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        def _build_task_tabs(self) -> None:
            for category, tasks in TASKS.items():
                panel = self.ttk_mod.Frame(self.notebook, style="Card.TFrame", padding=16)
                panel.columnconfigure(0, weight=1)
                panel.rowconfigure(1, weight=1)

                self.ttk_mod.Label(panel, text=f"{category} Tasks", style="CardTitle.TLabel").grid(
                    row=0, column=0, sticky="w"
                )

                canvas = self.tk_mod.Canvas(panel, bg="#ffffff", highlightthickness=0)
                scrollbar = self.ttk_mod.Scrollbar(panel, orient="vertical", command=canvas.yview)
                task_frame = self.ttk_mod.Frame(canvas, style="Card.TFrame")
                canvas_window = canvas.create_window((0, 0), window=task_frame, anchor="nw")

                task_frame.bind(
                    "<Configure>",
                    lambda event, task_canvas=canvas: task_canvas.configure(scrollregion=task_canvas.bbox("all")),
                )
                canvas.bind(
                    "<Configure>",
                    lambda event, task_canvas=canvas, window=canvas_window: task_canvas.itemconfigure(
                        window, width=event.width
                    ),
                )
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
                scrollbar.grid(row=1, column=1, sticky="ns", pady=(14, 0))

                self._build_rows(category, tasks, task_frame)
                self.notebook.add(panel, text=f"{category} ({len(tasks)})")

        def _build_rows(self, category: str, tasks: list[Task], parent) -> None:
            parent.columnconfigure(1, weight=1)
            self.task_vars[category] = []

            self.ttk_mod.Label(parent, text="Done", style="Header.TLabel", padding=(8, 6)).grid(row=0, column=0,
                                                                                                sticky="ew")
            self.ttk_mod.Label(parent, text="Task", style="Header.TLabel", padding=(8, 6)).grid(row=0, column=1,
                                                                                                sticky="ew")
            self.ttk_mod.Label(parent, text="Priority", style="Header.TLabel", padding=(8, 6)).grid(row=0, column=2,
                                                                                                    sticky="ew")
            self.ttk_mod.Label(parent, text="Status", style="Header.TLabel", padding=(8, 6)).grid(row=0, column=3,
                                                                                                  sticky="ew")
            self.ttk_mod.Label(parent, text="Action", style="Header.TLabel", padding=(8, 6)).grid(row=0, column=4,
                                                                                                  sticky="ew")

            for row, task in enumerate(tasks, start=1):
                done_var = self.tk_mod.BooleanVar(value=task.done)
                status_label = self.ttk_mod.Label(parent, text=task.status, style="Status.TLabel", padding=(8, 8))

                initial_style = "DoneTask.TLabel" if task.done else "Task.TLabel"
                task_label = self.ttk_mod.Label(parent, text=task.name, style=initial_style, padding=(8, 8),
                                                wraplength=450)

                done_var.trace_add(
                    "write",
                    lambda *_args, t=task, v=done_var, sl=status_label, tl=task_label: self._change_status(
                        t, v, sl, tl
                    ),
                )

                self.ttk_mod.Checkbutton(parent, variable=done_var).grid(row=row, column=0, sticky="w", padx=(8, 4),
                                                                         pady=4)
                task_label.grid(row=row, column=1, sticky="ew", pady=4)
                self.ttk_mod.Label(parent, text=task.priority, style=f"{task.priority}.TLabel", padding=(8, 4)).grid(
                    row=row, column=2, sticky="w", padx=(8, 16), pady=4
                )
                status_label.grid(row=row, column=3, sticky="w", pady=4, padx=(0, 12))

                self.ttk_mod.Button(
                    parent,
                    text="Delete",
                    style="Danger.TButton",
                    command=lambda c=category, t=task: self._delete_task(c, t)
                ).grid(row=row, column=4, sticky="e", pady=4)

                self.task_vars[category].append((task, done_var, status_label, task_label))

        def _change_status(self, task: Task, variable, status_label, task_label) -> None:
            is_done = bool(variable.get())
            task.done = is_done
            status_label.configure(text=task.status)

            if is_done:
                task_label.configure(style="DoneTask.TLabel")
            else:
                task_label.configure(style="Task.TLabel")

            self._update_summary()

        def _open_add_task_dialog(self) -> None:
            dialog = self.tk_mod.Toplevel(self)
            dialog.title("Add New Task")
            dialog.geometry("450x260")
            dialog.configure(bg="#ffffff")
            dialog.transient(self)
            dialog.grab_set()

            self.ttk_mod.Label(dialog, text="Task Name:", background="#ffffff", font=("Arial", 10, "bold")).pack(
                pady=(16, 4), padx=20, anchor="w")
            name_entry = self.ttk_mod.Entry(dialog, width=50, font=("Arial", 10))
            name_entry.pack(padx=20, anchor="w")
            name_entry.focus()

            controls_frame = self.ttk_mod.Frame(dialog, style="Card.TFrame")
            controls_frame.pack(fill="x", padx=20, pady=(16, 0))

            self.ttk_mod.Label(controls_frame, text="Category:", background="#ffffff").grid(row=0, column=0, sticky="w",
                                                                                            pady=4)
            cat_cb = self.ttk_mod.Combobox(controls_frame, values=list(TASKS.keys()), state="readonly", width=18)
            cat_cb.current(0)
            cat_cb.grid(row=1, column=0, sticky="w", padx=(0, 20))

            self.ttk_mod.Label(controls_frame, text="Priority:", background="#ffffff").grid(row=0, column=1, sticky="w",
                                                                                            pady=4)
            pri_cb = self.ttk_mod.Combobox(controls_frame, values=["High", "Medium", "Low"], state="readonly", width=15)
            pri_cb.current(1)
            pri_cb.grid(row=1, column=1, sticky="w")

            btn_frame = self.ttk_mod.Frame(dialog, style="Card.TFrame")
            btn_frame.pack(fill="x", side="bottom", pady=20, padx=20)

            def save_new_task():
                name = name_entry.get().strip()
                if not name:
                    self.msg_mod.showwarning("Warning", "Please enter a task name.", parent=dialog)
                    return

                category = cat_cb.get()
                priority = pri_cb.get()

                TASKS[category].append(Task(name, priority))
                self._refresh_ui()
                dialog.destroy()

            self.ttk_mod.Button(btn_frame, text="Save Task", style="Primary.TButton", command=save_new_task).pack(
                side="right", padx=(8, 0))
            self.ttk_mod.Button(btn_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(
                side="right")

        def _delete_task(self, category: str, task: Task) -> None:
            if self.msg_mod.askyesno("Confirm Delete", f"Are you sure you want to delete:\n\n'{task.name}'?"):
                TASKS[category].remove(task)
                self._refresh_ui()

        def _refresh_ui(self) -> None:
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            self.task_vars.clear()

            self._build_task_tabs()
            self._update_summary()

        def _update_summary(self) -> None:
            total_tasks = 0
            total_done = 0
            lines = []

            for category, rows in self.task_vars.items():
                task_count = len(rows)
                done_count = sum(1 for task, _v, _s, _t in rows if task.done)
                total_tasks += task_count
                total_done += done_count
                lines.append(f"{category}\n  {done_count}/{task_count} done\n")

            lines.append(f"Total\n  {total_done}/{total_tasks} done")

            self.summary_text.configure(state="normal")
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", "\n".join(lines))
            self.summary_text.configure(state="disabled")

        def _export_markdown(self) -> None:
            path = export_markdown(TASKS)
            self.msg_mod.showinfo("Export Complete", f"Markdown file created:\n{path}")

        def _reset_statuses(self) -> None:
            for rows in self.task_vars.values():
                for task, variable, status_label, task_label in rows:
                    task.done = False
                    variable.set(False)
                    status_label.configure(text=task.status)
                    task_label.configure(style="Task.TLabel")
            self._update_summary()

    app = TaskChartDesktopApp(tk, ttk, messagebox)
    app.mainloop()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open the Task Chart desktop app or export Markdown.")
    parser.add_argument("--export", action="store_true", help="Export task_chart.md without opening the desktop app.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.export:
        path = export_markdown(TASKS)
        print(f"Markdown file created: {path}")
        return 0

    return run_desktop_app()


if __name__ == "__main__":
    sys.exit(main())