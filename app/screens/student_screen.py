"""
Student Management screen.

Same student_service calls as before Batch 3 — only the presentation
changed (cards instead of a plain LabelFrame, striped table, styled
buttons). All validation/logging/error-handling behavior is unchanged.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_card, build_breadcrumb, style_treeview_stripes, stripe_tag


class StudentScreen(tk.Frame):
    def __init__(self, parent, fonts, go_home=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self.go_home = go_home
        self._build_header()
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        if self.go_home:
            build_breadcrumb(header, "Students", self.go_home, self.fonts)
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=16)
        tk.Label(inner, text="Student Management", bg=COLORS["header_bg"],
                  fg=COLORS["text_dark"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Add and review hosteller records.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=24, pady=(16, 0))
        content = build_card(wrapper, "Add Student", self.fonts)

        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Name", style="FormLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.name_var = tk.StringVar()
        ttk.Entry(content, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Registration No.", style="FormLabel.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.reg_var = tk.StringVar()
        ttk.Entry(content, textvariable=self.reg_var).grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Contact No.", style="FormLabel.TLabel").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        self.contact_var = tk.StringVar()
        ttk.Entry(content, textvariable=self.contact_var).grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Button(content, text="+  Add Student", style="Primary.TButton",
                    command=self.on_add).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content = build_card(wrapper, "All Students", self.fonts)

        columns = ("id", "name", "reg_no", "contact")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        for col, label, width in zip(columns, ("ID", "Name", "Registration No.", "Contact"),
                                       (50, 220, 160, 140)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_stripes(self.tree)

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
        for i, student in enumerate(student_service.get_all_students()):
            self.tree.insert("", "end", values=(
                student["student_id"], student["name"],
                student["registration_number"], student["contact_number"],
            ), tags=(stripe_tag(i),))
