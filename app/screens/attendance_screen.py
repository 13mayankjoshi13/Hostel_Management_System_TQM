"""Staff roll call: mark Present / Absent for each allocated student."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import attendance_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, keep_selection, section_header, build_panel, build_table, status_tag, style_treeview_status_tags


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
        buttons = tk.Frame(content, bg=COLORS["surface"])
        buttons.pack(anchor="e", pady=(10, 0))
        ttk.Button(buttons, text="Mark Present", style="Primary.TButton",
                   command=lambda: self.mark("Present")).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Mark Absent", style="Secondary.TButton",
                   command=lambda: self.mark("Absent")).pack(side="left")

    def mark(self, status):
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
