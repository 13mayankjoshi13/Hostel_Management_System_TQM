"""Leave Tracking screen: which student is on leave, from which room."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import allocation_service, leave_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags


class LeaveScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._student_options = {}
        section_header(self, "Leave Tracking",
                        "Record which hosteller is on leave and mark them returned.", fonts)
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

        self.from_var = tk.StringVar(value=date.today().isoformat())
        form_row(wrapper, self.fonts, 1, "From (YYYY-MM-DD)", ttk.Entry(wrapper, textvariable=self.from_var))
        self.to_var = tk.StringVar(value=date.today().isoformat())
        form_row(wrapper, self.fonts, 2, "To (YYYY-MM-DD)", ttk.Entry(wrapper, textvariable=self.to_var))
        self.reason_var = tk.StringVar()
        form_row(wrapper, self.fonts, 3, "Reason", ttk.Entry(wrapper, textvariable=self.reason_var))

        ttk.Button(wrapper, text="Record Leave", style="Primary.TButton",
                    command=self.on_record).grid(row=4, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "Leaves", self.fonts)
        self.tree = build_table(content, ("id", "student", "room", "from", "to", "reason", "status"),
                                  ("ID", "Student", "Room", "From", "To", "Reason", "Status"),
                                  (45, 160, 70, 90, 90, 170, 90), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        ttk.Button(content, text="Mark Returned", style="Primary.TButton",
                    command=self.on_return).pack(anchor="e", pady=(10, 0))

    def on_record(self):
        student_id = self._student_options.get(self.student_var.get())
        try:
            leave_service.record_leave(student_id, self.from_var.get(), self.to_var.get(), self.reason_var.get())
            self.reason_var.set("")
            self.refresh_table()
            messagebox.showinfo("Success", "Leave recorded.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Leave", "record_leave_ui", e)

    def on_return(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a leave first.")
            return
        leave_id = self.tree.item(selected[0])["values"][0]
        try:
            leave_service.mark_returned(leave_id)
            self.refresh_table()
            messagebox.showinfo("Success", "Marked as returned.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Leave", "mark_returned_ui", e)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for leave in leave_service.get_all_leaves():
            self.tree.insert("", "end", values=(
                leave["leave_id"], leave["student_name"], leave["room_number"],
                leave["from_date"], leave["to_date"], leave["reason"], leave["status"],
            ), tags=("default",))

    def refresh(self):
        self._student_options = {
            f"{a['student_name']} — Room {a['room_number']}": a["student_id"]
            for a in allocation_service.get_active_allocations()
        }
        self.student_combo["values"] = list(self._student_options.keys())
        self.refresh_table()
