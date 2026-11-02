"""Leave Tracking screen: which student is on leave, from which room."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox, simpledialog

from app.services import allocation_service, leave_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import keep_selection, COLORS, status_tag, section_header, form_row, build_panel, build_table, style_treeview_status_tags, form_card, split_layout


class LeaveScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._student_options = {}
        section_header(self, "Leave Tracking",
                        "Approve student leave requests, record leaves and mark hostellers returned.", fonts)
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Record a leave", self.fonts)

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
        wrapper = tk.Frame(self.right, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)
        content = build_panel(wrapper, "Leaves", self.fonts)
        self.tree = build_table(content, ("id", "student", "room", "from", "to", "reason", "status"),
                                  ("ID", "Student", "Room", "From", "To", "Reason", "Status"),
                                  (45, 160, 70, 90, 90, 170, 90), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_leave_select(event=None):
            sel = self.tree.selection()
            if not sel: return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Leave #{vals[0]} — {vals[1]}",
                    fields={
                        "Leave ID": vals[0],
                        "Student": vals[1],
                        "Room": vals[2],
                        "From Date": vals[3],
                        "To Date": vals[4],
                        "Status": vals[6],
                    },
                    full_text=f"Reason: {vals[5]}"
                )

        self.tree.bind("<Double-Button-1>", _on_leave_select)
        self.tree.bind("<Return>", _on_leave_select)

        buttons = tk.Frame(content, bg=COLORS["surface"])
        buttons.pack(anchor="e", pady=(10, 0))
        if session.get_role() in session.WARDEN_ROLES:
            ttk.Button(buttons, text="Approve", style="Primary.TButton",
                       command=lambda: self.on_decide(True)).pack(side="left", padx=(0, 8))
            ttk.Button(buttons, text="Reject", style="Secondary.TButton",
                       command=lambda: self.on_decide(False)).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Mark Returned", style="Primary.TButton", command=self.on_return).pack(side="left")


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

    def on_decide(self, approve: bool):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a leave first.")
            return
        note = "" if approve else simpledialog.askstring("Reject leave", "Reason for rejecting:", parent=self)
        if note is None:
            return
        try:
            leave_service.decide_leave(self.tree.item(selected[0])["values"][0], approve, note)
            self.refresh_table()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Leave", "decide_leave_ui", e)

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
        keep_selection(self.tree, self._rebuild_table)

    def _rebuild_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for leave in leave_service.get_all_leaves():
            self.tree.insert("", "end", values=(
                leave["leave_id"], leave["student_name"], leave["room_number"],
                leave["from_date"], leave["to_date"], leave["reason"], leave["status"],
            ), tags=(status_tag(leave["status"]),))

    def refresh(self):
        if session.get_role() not in session.STAFF_ROLES:
            return
        self._student_options = {
            f"{a['student_name']} — Room {a['room_number']}": a["student_id"]
            for a in allocation_service.get_active_allocations()
        }
        self.student_combo["values"] = list(self._student_options.keys())
        self.refresh_table()
