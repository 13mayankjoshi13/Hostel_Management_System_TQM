"""Visitor log screen: check visitors in and out at the gate."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import allocation_service, visitor_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, keep_selection, section_header, form_row, build_panel, build_table, form_card,
                       split_layout, style_treeview_status_tags)


class VisitorScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._students = {}
        section_header(self, "Visitors", "Log who visits which student. Visits outside 9 AM - 7 PM are flagged.", fonts)
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Check in a visitor", self.fonts)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(wrapper, textvariable=self.student_var, state="readonly")
        form_row(wrapper, self.fonts, 0, "Student visited", self.student_combo)
        self.name_var = tk.StringVar()
        form_row(wrapper, self.fonts, 1, "Visitor name", ttk.Entry(wrapper, textvariable=self.name_var))
        self.relation_var = tk.StringVar(value=visitor_service.RELATIONS[0])
        form_row(wrapper, self.fonts, 2, "Relation",
                 ttk.Combobox(wrapper, textvariable=self.relation_var, values=visitor_service.RELATIONS, state="readonly"))
        self.phone_var = tk.StringVar()
        form_row(wrapper, self.fonts, 3, "Phone (optional)", ttk.Entry(wrapper, textvariable=self.phone_var))
        self.purpose_var = tk.StringVar()
        form_row(wrapper, self.fonts, 4, "Purpose", ttk.Entry(wrapper, textvariable=self.purpose_var))
        ttk.Button(wrapper, text="Check In", style="Primary.TButton",
                   command=self.on_check_in).grid(row=5, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        content = build_panel(self.right, "Visitor log", self.fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        self.inside_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Inside now only", variable=self.inside_var, command=self.refresh).pack(side="left")
        self.summary = tk.Label(bar, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["label"])
        self.summary.pack(side="right")
        self.tree = build_table(content, ("id", "student", "room", "visitor", "relation", "in", "out", "flag"),
                                ("ID", "Student", "Room", "Visitor", "Relation", "In", "Out", "Flag"),
                                (40, 130, 60, 130, 80, 100, 100, 90), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.tag_configure("flagged", foreground=COLORS["danger"])
        ttk.Button(content, text="Check Out", style="Primary.TButton",
                   command=self.on_check_out).pack(anchor="e", pady=(10, 0))

    def on_check_in(self):
        try:
            visitor_service.log_visitor(self._students.get(self.student_var.get()), self.name_var.get(),
                                        self.relation_var.get(), self.phone_var.get(), self.purpose_var.get())
            for var in (self.name_var, self.phone_var, self.purpose_var):
                var.set("")
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Visitor", "log_visitor_ui", e)

    def on_check_out(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a visitor first.")
            return
        try:
            visitor_service.check_out(self.tree.item(selected[0])["values"][0])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Visitor", "check_out_ui", e)

    def refresh(self):
        if session.get_role() not in session.VISITOR_ROLES:
            return
        self._students = {f"{a['student_name']} — Room {a['room_number']}": a["student_id"]
                          for a in visitor_service.visit_targets()}
        self.student_combo["values"] = list(self._students)
        keep_selection(self.tree, self._rebuild)

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for v in visitor_service.list_visitors(self.inside_var.get()):
            self.tree.insert("", "end", values=(v["visitor_id"], v["student_name"], v["room_number"], v["visitor_name"],
                                                v["relation"], v["in_time"][5:16], v["out_time"][5:16] if v["out_time"] else "Inside", v["flag"]),
                             tags=("flagged" if v["flag"] else "default",))
        self.summary.config(text=f"Inside now: {visitor_service.inside_count()}")
