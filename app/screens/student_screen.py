"""
Student Management screen. Same student_service calls as every prior
batch — only the presentation changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags


class StudentScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Students", "Add and review hosteller records.", fonts)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)

        self.name_var = tk.StringVar()
        self.reg_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        form_row(wrapper, self.fonts, 0, "Name", ttk.Entry(wrapper, textvariable=self.name_var))
        form_row(wrapper, self.fonts, 1, "Registration No.", ttk.Entry(wrapper, textvariable=self.reg_var))
        form_row(wrapper, self.fonts, 2, "Contact No.", ttk.Entry(wrapper, textvariable=self.contact_var))

        ttk.Button(wrapper, text="Add Student", style="Primary.TButton",
                    command=self.on_add).grid(row=3, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "All Students", self.fonts)

        self.tree = build_table(content, ("id", "name", "reg_no", "contact"),
                                  ("ID", "Name", "Registration No.", "Contact"),
                                  (50, 240, 170, 150), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

    def on_add(self):
        try:
            student_service.add_student(
                self.name_var.get(), self.reg_var.get(), self.contact_var.get()
            )
            self.name_var.set("")
            self.reg_var.set("")
            self.contact_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Student added successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Student", "add_student_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in student_service.get_all_students():
            self.tree.insert("", "end", values=(
                student["student_id"], student["name"],
                student["registration_number"], student["contact_number"],
            ), tags=("default",))
