"""
Bug Tracker screen (Q09 feature #4). Same unboxed-form + table-panel
pattern as every other screen since Batch 6. The status pipeline is
entirely enforced by bug_service — this screen just calls it.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.services import bug_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, style_treeview_status_tags, status_tag

_MODULES = ["Student", "Room", "Allocation", "Complaint", "Database", "UI", "Other"]
_CATEGORIES = ["Functional", "UI/UX", "Validation", "Performance", "Data Integrity", "Security", "Other"]
_SEVERITIES = ["Low", "Medium", "High", "Critical"]
_PRIORITIES = ["Low", "Medium", "High"]


class BugScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._bug_rows = {}
        section_header(self, "Bug Tracker",
                        "Log, work, and verify fixes for defects found during testing.", fonts)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)

        self.module_var = tk.StringVar(value=_MODULES[0])
        form_row(wrapper, self.fonts, 0, "Module", ttk.Combobox(
            wrapper, textvariable=self.module_var, values=_MODULES, state="readonly"))

        self.category_var = tk.StringVar(value=_CATEGORIES[0])
        form_row(wrapper, self.fonts, 1, "Category", ttk.Combobox(
            wrapper, textvariable=self.category_var, values=_CATEGORIES, state="readonly"))

        self.title_var = tk.StringVar()
        form_row(wrapper, self.fonts, 2, "Title", ttk.Entry(wrapper, textvariable=self.title_var))

        self.description_text = tk.Text(wrapper, height=3, wrap="word", font=self.fonts["body"],
                                          relief="solid", bd=1, bg=COLORS["surface"],
                                          fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                                          highlightbackground=COLORS["border_strong"],
                                          highlightcolor=COLORS["accent"])
        form_row(wrapper, self.fonts, 3, "Description", self.description_text)

        self.severity_var = tk.StringVar(value=_SEVERITIES[0])
        form_row(wrapper, self.fonts, 4, "Severity", ttk.Combobox(
            wrapper, textvariable=self.severity_var, values=_SEVERITIES, state="readonly"))

        self.priority_var = tk.StringVar(value=_PRIORITIES[0])
        form_row(wrapper, self.fonts, 5, "Priority", ttk.Combobox(
            wrapper, textvariable=self.priority_var, values=_PRIORITIES, state="readonly"))

        ttk.Button(wrapper, text="Log Bug", style="Primary.TButton",
                    command=self.on_log).grid(row=6, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "All Bugs", self.fonts)

        columns = ("id", "module", "title", "severity", "priority", "status", "date")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        for col, label, width in zip(
            columns, ("ID", "Module", "Title", "Severity", "Priority", "Status", "Date"),
            (45, 90, 260, 80, 80, 100, 100),
        ):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        button_row = tk.Frame(content, bg=COLORS["surface"])
        button_row.pack(anchor="e", pady=(10, 0))
        ttk.Button(button_row, text="Start Progress", style="Secondary.TButton",
                    command=self.on_start_progress).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Mark Fixed", style="Secondary.TButton",
                    command=self.on_mark_fixed).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Close Bug", style="Primary.TButton",
                    command=self.on_close).pack(side="left")

    def on_log(self):
        description = self.description_text.get("1.0", "end").strip()
        try:
            bug_service.log_bug(
                self.module_var.get(), self.category_var.get(), self.title_var.get(),
                description, self.severity_var.get(), self.priority_var.get(),
            )
            self.title_var.set("")
            self.description_text.delete("1.0", "end")
            self.refresh()
            messagebox.showinfo("Success", "Bug logged successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Bug", "log_bug_ui", e)

    def _get_selected_bug(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a bug first.")
            return None
        return self._bug_rows.get(selected[0])

    def on_start_progress(self):
        bug = self._get_selected_bug()
        if bug is None:
            return
        try:
            bug_service.start_progress(bug["bug_id"])
            self.refresh()
            messagebox.showinfo("Success", "Bug moved to In Progress.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Bug", "start_progress_ui", e)

    def on_mark_fixed(self):
        bug = self._get_selected_bug()
        if bug is None:
            return
        root_cause = simpledialog.askstring("Mark Fixed", "Root cause:", parent=self)
        if root_cause is None:
            return
        corrective_action = simpledialog.askstring("Mark Fixed", "Corrective action:", parent=self)
        if corrective_action is None:
            return
        test_case = simpledialog.askstring("Mark Fixed", "Test case (file::test_name):", parent=self)
        if test_case is None:
            return
        try:
            bug_service.mark_fixed(bug["bug_id"], root_cause, corrective_action, test_case)
            self.refresh()
            messagebox.showinfo("Success", "Bug marked as fixed.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Bug", "mark_fixed_ui", e)

    def on_close(self):
        bug = self._get_selected_bug()
        if bug is None:
            return
        try:
            bug_service.close_bug(bug["bug_id"])
            self.refresh()
            messagebox.showinfo("Success", "Bug closed.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Bug", "close_bug_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._bug_rows = {}
        for bug in bug_service.get_all_bugs():
            item_id = self.tree.insert("", "end", values=(
                bug["bug_id"], bug["module"], bug["title"], bug["severity"],
                bug["priority"], bug["status"], bug["date"],
            ), tags=(status_tag(bug["status"]),))
            self._bug_rows[item_id] = bug
