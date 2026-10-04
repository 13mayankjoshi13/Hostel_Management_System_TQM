"""
Complaint Management screen. Status flow still enforced entirely by
complaint_service — this screen only calls it and shows the result.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.services import student_service, complaint_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags, status_tag

_CATEGORIES = ["Maintenance", "Cleanliness", "Noise", "Security", "Food", "Other"]


class ComplaintScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._student_options = {}
        self._complaint_rows = {}
        section_header(self, "Complaints", "Log, assign, and resolve hosteller complaints.", fonts)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)

        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(wrapper, textvariable=self.student_var, state="readonly")
        form_row(wrapper, self.fonts, 0, "Student", self.student_combo)

        self.category_var = tk.StringVar(value=_CATEGORIES[0])
        form_row(wrapper, self.fonts, 1, "Category", ttk.Combobox(
            wrapper, textvariable=self.category_var, values=_CATEGORIES, state="readonly"))

        self.description_text = tk.Text(wrapper, height=3, wrap="word", font=self.fonts["body"],
                                          relief="solid", bd=1, bg=COLORS["surface"],
                                          fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                                          highlightbackground=COLORS["border_strong"],
                                          highlightcolor=COLORS["accent"])
        form_row(wrapper, self.fonts, 2, "Description", self.description_text)

        button_row = tk.Frame(wrapper, bg=COLORS["background"])
        button_row.grid(row=3, column=1, sticky="w", pady=(10, 0))
        ttk.Button(button_row, text="Log Complaint", style="Primary.TButton",
                    command=self.on_create).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Students", style="Secondary.TButton",
                    command=self.refresh_student_dropdown).pack(side="left")

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "All Complaints", self.fonts)

        self.tree = build_table(
            content, ("id", "student", "category", "status", "assigned_to", "created_at"),
            ("ID", "Student", "Category", "Status", "Assigned To", "Created At"),
            (45, 160, 110, 90, 140, 150), height=7,
        )
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        button_row = tk.Frame(content, bg=COLORS["surface"])
        button_row.pack(anchor="e", pady=(10, 0))
        ttk.Button(button_row, text="Assign Selected", style="Secondary.TButton",
                    command=self.on_assign).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Resolve Selected", style="Primary.TButton",
                    command=self.on_resolve).pack(side="left")

    def refresh_student_dropdown(self):
        self._student_options = {
            f"{s['student_id']} — {s['name']} ({s['registration_number']})": s["student_id"]
            for s in student_service.get_all_students()
        }
        self.student_combo["values"] = list(self._student_options.keys())

    def on_create(self):
        student_label = self.student_var.get()
        if not student_label:
            messagebox.showerror("Invalid Input", "Please select a student.")
            return
        student_id = self._student_options.get(student_label)
        description = self.description_text.get("1.0", "end").strip()

        try:
            complaint_service.create_complaint(student_id, self.category_var.get(), description)
            self.description_text.delete("1.0", "end")
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint logged successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "create_complaint_ui", e)

    def _get_selected_complaint(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a complaint first.")
            return None
        return self._complaint_rows.get(selected[0])

    def on_assign(self):
        complaint = self._get_selected_complaint()
        if complaint is None:
            return
        assigned_to = simpledialog.askstring("Assign Complaint", "Assign to (staff name):", parent=self)
        if assigned_to is None:
            return
        try:
            complaint_service.assign_complaint(complaint["complaint_id"], assigned_to)
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint assigned.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "assign_complaint_ui", e)

    def on_resolve(self):
        complaint = self._get_selected_complaint()
        if complaint is None:
            return
        notes = simpledialog.askstring("Resolve Complaint", "Resolution notes:", parent=self)
        if notes is None:
            return
        try:
            complaint_service.resolve_complaint(complaint["complaint_id"], notes)
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint resolved.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "resolve_complaint_ui", e)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._complaint_rows = {}
        for complaint in complaint_service.get_all_complaints():
            item_id = self.tree.insert("", "end", values=(
                complaint["complaint_id"], complaint["student_name"], complaint["category"],
                complaint["status"], complaint["assigned_to"] or "—", complaint["created_at"],
            ), tags=(status_tag(complaint["status"]),))
            self._complaint_rows[item_id] = complaint

    def refresh(self):
        self.refresh_student_dropdown()
        self.refresh_table()
