"""
Student Management screen. Same student_service calls as every prior
batch — only the presentation changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags, form_card, split_layout, button_row


class StudentScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Students", "Add, edit and review hosteller records.", fonts)
        self._editing_id = None
        self._restoring = False
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Add a student", self.fonts)

        self.name_var = tk.StringVar()
        self.reg_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        form_row(wrapper, self.fonts, 0, "Name", ttk.Entry(wrapper, textvariable=self.name_var))
        form_row(wrapper, self.fonts, 1, "Registration No.", ttk.Entry(wrapper, textvariable=self.reg_var))
        form_row(wrapper, self.fonts, 2, "Contact No.", ttk.Entry(wrapper, textvariable=self.contact_var))

        buttons = button_row(wrapper, 3)
        ttk.Button(buttons, text="Add Student", style="Primary.TButton", command=self.on_add).pack(side="left")
        self.save_button = ttk.Button(buttons, text="Save Changes", style="Secondary.TButton",
                                       command=self.on_save, state="disabled")
        self.save_button.pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Clear", style="Secondary.TButton",
                    command=self.on_clear).pack(side="left", padx=(8, 0))
        tk.Label(wrapper, text="Select a student in the table to edit their details.", bg=wrapper.cget("bg"),
                  fg=COLORS["text_tertiary"], font=self.fonts["label"]).grid(row=4, column=1, sticky="w", pady=(8, 0))

    def _build_table(self):
        wrapper = tk.Frame(self.right, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)
        content = build_panel(wrapper, "All Students", self.fonts)
        sort_row = tk.Frame(content, bg=COLORS["surface"])
        sort_row.pack(fill="x", pady=(0, 8))
        tk.Label(sort_row, text="Sort by", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=self.fonts["label"]).pack(side="left", padx=(0, 8))
        self.sort_var = tk.StringVar(value="Newest first")
        sort_box = ttk.Combobox(sort_row, textvariable=self.sort_var, values=list(student_service.SORT_OPTIONS),
                                 state="readonly", width=18)
        sort_box.pack(side="left")
        sort_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.tree = build_table(content, ("id", "name", "reg_no", "contact"),
                                  ("ID", "Name", "Registration No.", "Contact"),
                                  (50, 240, 170, 150), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected or self._restoring:
            return
        values = self.tree.item(selected[0], "values")
        self._editing_id = int(values[0])
        self.name_var.set(values[1])
        self.reg_var.set(values[2])
        self.contact_var.set(values[3])
        self.save_button.state(["!disabled"])

    def on_clear(self):
        self._editing_id = None
        for var in (self.name_var, self.reg_var, self.contact_var):
            var.set("")
        self.tree.selection_remove(self.tree.selection())
        self.save_button.state(["disabled"])

    def on_save(self):
        if self._editing_id is None:
            return
        try:
            student_service.update_student(self._editing_id, self.name_var.get(),
                                            self.reg_var.get(), self.contact_var.get())
            self.on_clear()
            self.refresh()
            messagebox.showinfo("Success", "Student details updated.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Student", "update_student_ui", e)

    def on_add(self):
        try:
            student_service.add_student(
                self.name_var.get(), self.reg_var.get(), self.contact_var.get()
            )
            self.on_clear()
            self.refresh()
            messagebox.showinfo("Success", "Student added successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Student", "add_student_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._restoring = True
        try:
            for student in student_service.get_all_students(self.sort_var.get()):
                item = self.tree.insert("", "end", values=(
                    student["student_id"], student["name"],
                    student["registration_number"], student["contact_number"],
                ), tags=("default",))
                if student["student_id"] == self._editing_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
            if self._editing_id is not None and not self.tree.selection():
                self._editing_id = None
                self.save_button.state(["disabled"])
        finally:
            self._restoring = False
