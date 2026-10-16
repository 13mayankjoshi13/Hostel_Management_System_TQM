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
from app.theme import COLORS, section_header, form_row, build_panel, style_treeview_status_tags, status_tag, form_card, split_layout, build_table

_MODULES = ["Student", "Room", "Allocation", "Complaint", "Database", "UI", "Other"]
_CATEGORIES = ["Functional", "UI/UX", "Validation", "Performance", "Data Integrity", "Security", "Other"]
_SEVERITIES = ["Low", "Medium", "High", "Critical"]
_PRIORITIES = ["Low", "Medium", "High"]
_FILTERS = {"All": None, "Open": ("Open", "In Progress"), "Solved": ("Fixed", "Closed")}


class BugScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._bug_rows = {}
        section_header(self, "Bug Tracker",
                        "Log, work, and verify fixes for defects found during testing.", fonts)
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Log a bug", self.fonts)

        self.module_var = tk.StringVar(value=_MODULES[0])
        form_row(wrapper, self.fonts, 0, "Module", ttk.Combobox(
            wrapper, textvariable=self.module_var, values=_MODULES, state="readonly"))

        self.category_var = tk.StringVar(value=_CATEGORIES[0])
        form_row(wrapper, self.fonts, 1, "Category", ttk.Combobox(
            wrapper, textvariable=self.category_var, values=_CATEGORIES, state="readonly"))

        self.title_var = tk.StringVar()
        form_row(wrapper, self.fonts, 2, "Title", ttk.Entry(wrapper, textvariable=self.title_var))

        self.description_text = tk.Text(wrapper, height=3, wrap="word", font=self.fonts["body"],
                                          relief="flat", bd=0, padx=8, pady=6, bg=COLORS["surface"],
                                          fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                                          highlightthickness=1, highlightbackground=COLORS["border_strong"],
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
        wrapper = tk.Frame(self.right, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)
        content = build_panel(wrapper, "Bugs", self.fonts)

        filter_row = tk.Frame(content, bg=COLORS["surface"])
        filter_row.pack(fill="x", pady=(0, 8))
        tk.Label(filter_row, text="Show", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=self.fonts["label"]).pack(side="left", padx=(0, 8))
        self.filter_var = tk.StringVar(value="All")
        filter_box = ttk.Combobox(filter_row, textvariable=self.filter_var, values=list(_FILTERS),
                                   state="readonly", width=12)
        filter_box.pack(side="left")
        filter_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.count_label = tk.Label(filter_row, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                                     font=self.fonts["label"])
        self.count_label.pack(side="right")

        self.tree = build_table(content, ("id", "title", "severity", "status", "reported", "fixed", "date"),
                                  ("ID", "Title", "Severity", "Status", "Reported", "Fixed by", "Date"),
                                  (34, 270, 66, 70, 74, 74, 84), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.detail = tk.Label(content, text="Select a bug to see how it was found and fixed.", anchor="nw",
                                justify="left", wraplength=520, bg=COLORS["surface"],
                                fg=COLORS["text_secondary"], font=self.fonts["label"])
        self.detail.pack(fill="x", pady=(10, 0))

        button_row = tk.Frame(content, bg=COLORS["surface"])
        button_row.pack(anchor="e", pady=(10, 0))
        ttk.Button(button_row, text="Start Progress", style="Secondary.TButton",
                    command=self.on_start_progress).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Mark Fixed", style="Secondary.TButton",
                    command=self.on_mark_fixed).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Close Bug", style="Primary.TButton",
                    command=self.on_close).pack(side="left")

    def on_select(self, _event=None):
        selected = self.tree.selection()
        bug = self._bug_rows.get(selected[0]) if selected else None
        if bug is None:
            return
        lines = [f"{bug['title']}  ({bug['module']} · {bug['category']} · {bug['severity']}/{bug['priority']})",
                 f"Found: {bug['description']}",
                 f"Reported by {bug.get('reported_by') or '—'} on {bug['date']}"]
        if bug["status"] in ("Fixed", "Closed"):
            lines += [f"Root cause: {bug.get('root_cause') or '—'}",
                      f"Fix: {bug.get('corrective_action') or '—'}",
                      f"Test: {bug.get('test_case') or '—'}",
                      f"Fixed by {bug.get('fixed_by') or '—'}"]
        self.detail.configure(text="\n".join(lines))

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
        bugs = bug_service.get_all_bugs()
        wanted = _FILTERS[self.filter_var.get()]
        for bug in bugs:
            if wanted is not None and bug["status"] not in wanted:
                continue
            item_id = self.tree.insert("", "end", values=(
                bug["bug_id"], bug["title"], bug["severity"], bug["status"],
                bug.get("reported_by") or "—", bug.get("fixed_by") or "—", bug["date"],
            ), tags=(status_tag(bug["status"]),))
            self._bug_rows[item_id] = bug
        solved = sum(1 for b in bugs if b["status"] in _FILTERS["Solved"])
        open_count = sum(1 for b in bugs if b["status"] in _FILTERS["Open"])
        self.count_label.configure(text=f"{open_count} open · {solved} solved · {len(bugs)} total")
