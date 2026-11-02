"""Staff roll call: mark Present / Absent for each allocated student."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import attendance_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, keep_selection, section_header, build_panel, build_table,
                       status_tag, style_treeview_status_tags, chip)


class AttendanceScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Attendance", "Roll call for the selected day. Students on approved leave show as Leave.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        content = build_panel(wrapper, "Roll call", fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Date", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"]).pack(side="left", padx=(0, 8))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(bar, textvariable=self.date_var, width=12).pack(side="left")
        ttk.Button(bar, text="Load", style="Secondary.TButton", command=self.refresh).pack(side="left", padx=8)
        self.summary = tk.Label(bar, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.summary.pack(side="right")
        self.tree = build_table(content, ("id", "name", "reg", "room", "status"),
                                ("ID", "Student", "Registration No.", "Room", "Status"), (45, 200, 140, 80, 90), height=12)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_att_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Attendance Record: {vals[1]}",
                    fields={
                        "Student ID": vals[0],
                        "Name": vals[1],
                        "Registration No.": vals[2],
                        "Room": vals[3],
                        "Attendance Status": vals[4],
                        "Date": self.date_var.get(),
                    },
                    full_text=f"Roll call record for {vals[1]} on {self.date_var.get()}: status is currently marked as {vals[4]}."
                )

        self.tree.bind("<Double-Button-1>", _on_att_select)
        self.tree.bind("<Return>", _on_att_select)

        self.buttons = tk.Frame(content, bg=COLORS["surface"])

        self.buttons.pack(anchor="e", pady=(10, 0))
        self.btn_present = ttk.Button(self.buttons, text="Mark Present", style="Primary.TButton",
                                      command=lambda: self.mark("Present"))
        self.btn_absent = ttk.Button(self.buttons, text="Mark Absent", style="Secondary.TButton",
                                     command=lambda: self.mark("Absent"))
        self.view_only_notice = tk.Label(self.buttons,
                                         text="View-only mode: Only Administrator & Super Admin can mark attendance.",
                                         bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=fonts["small"])

    def mark(self, status):
        if session.get_role() not in session.ADMIN_ROLES:
            messagebox.showerror("Permission Denied", "Only Administrator and Super Admin can mark attendance.")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a student first.")
            return
        try:
            attendance_service.mark_attendance(self.tree.item(selected[0])["values"][0], self.date_var.get(), status)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Attendance", str(e))
        except Exception as e:
            handle_unexpected_error("Attendance", "mark_attendance_ui", e)

    def refresh(self):
        is_admin = session.get_role() in session.ADMIN_ROLES
        if is_admin:
            self.view_only_notice.pack_forget()
            self.btn_present.pack(side="left", padx=(0, 8))
            self.btn_absent.pack(side="left")
        else:
            self.btn_present.pack_forget()
            self.btn_absent.pack_forget()
            self.view_only_notice.pack(side="right")
        keep_selection(self.tree, self._rebuild)

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            roster = attendance_service.get_roster(self.date_var.get())
        except ValidationError as e:
            messagebox.showerror("Attendance", str(e))
            return
        counts = {"Present": 0, "Absent": 0, "Leave": 0, "Unmarked": 0}
        for r in roster:
            counts[r["status"]] += 1
            self.tree.insert("", "end", values=(r["student_id"], r["name"], r["registration_number"],
                                                 r["room_number"], r["status"]), tags=(status_tag(r["status"]),))
        self.summary.config(text="  ".join(f"{k}: {v}" for k, v in counts.items()))
