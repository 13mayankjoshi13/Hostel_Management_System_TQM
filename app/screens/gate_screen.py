"""Gate log screen: security marks students Out and In; late entries are flagged."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import gate_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, build_panel, build_table, form_card, form_row, keep_selection, section_header,
                       split_layout, style_treeview_status_tags)


class GateScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._students = {}
        section_header(self, "Gate Log", "Record students going out and coming in. Entries after 10 PM are flagged late.", fonts)
        self.left, self.right = split_layout(self)
        self.card = form_card(self.left, "Record a movement", fonts)
        self.student_var = tk.StringVar()
        self.combo = ttk.Combobox(self.card, textvariable=self.student_var, state="readonly")
        form_row(self.card, fonts, 0, "Student", self.combo)
        row = tk.Frame(self.card, bg=COLORS["surface"])
        row.grid(row=1, column=1, sticky="w", pady=(10, 0))
        self.out_button = ttk.Button(row, text="Mark Out", style="Secondary.TButton", command=lambda: self.log("Out"))
        self.in_button = ttk.Button(row, text="Mark In", style="Primary.TButton", command=lambda: self.log("In"))
        self.out_button.pack(side="left", padx=(0, 8))
        self.in_button.pack(side="left")
        self.status = tk.Label(self.card, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.status.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._status())
        content = build_panel(self.right, "Gate log", fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        self.late_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Late entries only", variable=self.late_var, command=self.refresh).pack(side="left")
        self.summary = tk.Label(bar, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.summary.pack(side="right")
        self.tree = build_table(content, ("student", "room", "dir", "time", "flag"),
                                ("Student", "Room", "Direction", "Time", "Flag"), (160, 70, 80, 150, 90), height=12)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.tag_configure("late", foreground=COLORS["danger"])

    def _status(self):
        sid = self._students.get(self.student_var.get())
        info = next((s for s in self._all if s["student_id"] == sid), None) if sid else None
        self.status.config(text="" if info is None else ("Currently out" if info["is_out"] else "Currently inside"))

    def log(self, direction):
        sid = self._students.get(self.student_var.get())
        try:
            gate_service.log_movement(sid, direction)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Gate log", str(e))
        except Exception as e:
            handle_unexpected_error("Gate", "log_movement_ui", e)

    def refresh(self):
        if session.get_role() not in session.GATE_ROLES:
            return
        self._all = gate_service.students_for_gate()
        self._students = {f"{s['student_name']} - Room {s['room_number']}": s["student_id"] for s in self._all}
        self.combo["values"] = list(self._students)
        self._status()
        keep_selection(self.tree, self._rebuild)
        c = gate_service.counts()
        self.summary.config(text=f"Out now: {c['out_now']}   Late today: {c['late_today']}")

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for g in gate_service.list_log(late_only=self.late_var.get()):
            self.tree.insert("", "end", values=(g["student_name"], g["room_number"], g["direction"], g["logged_at"],
                                                "Late entry" if g["late"] else ""), tags=("late" if g["late"] else "default",))
