"""Duty desk: the home page of Mess, Maintenance, Security and Housekeeping staff."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.services import complaint_service, duty_service, gate_service, mess_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, build_panel, build_table, kpi_row, keep_selection, section_header, status_tag,
                       style_treeview_status_tags)

_SUBTITLES = {"Mess Staff": "Food complaints and today's mess work.",
              "Maintenance Staff": "Maintenance and washroom complaints.",
              "Housekeeping Staff": "Cleanliness complaints and today's cleaning.",
              "Security Staff": "Who is out of the hostel and who came in late."}


class DutyScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Duty", "Your work queue.", fonts)
        self.kpis = tk.Frame(self, bg=COLORS["background"])
        self.kpis.pack(fill="x", padx=28, pady=(0, 12))
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.panel = build_panel(wrapper, "Queue", fonts)
        self.qpanel = build_panel(wrapper, "Mess queue", fonts)
        self.qtree = build_table(self.qpanel, ("id", "student", "room", "meal", "joined"),
                                 ("#", "Student", "Room", "Meal", "Joined"), (40, 180, 80, 90, 140), height=6)
        self.qtree.pack(fill="both", expand=True)
        qbtns = tk.Frame(self.qpanel, bg=COLORS["surface"])
        qbtns.pack(anchor="e", pady=(10, 0))
        ttk.Button(qbtns, text="Clear Queue", style="Secondary.TButton", command=self.on_clear).pack(side="left", padx=(0, 8))
        ttk.Button(qbtns, text="Serve Next", style="Secondary.TButton", command=self.on_serve_next).pack(side="left", padx=(0, 8))
        ttk.Button(qbtns, text="Mark Served", style="Primary.TButton", command=self.on_serve).pack(side="left")
        self.qpanel.master.pack_forget()
        self.tree = None
        self.buttons = tk.Frame(self.panel, bg=COLORS["surface"])
        self._mode = None

    def _build_table(self, mode):
        if self._mode == mode:
            return
        self._mode = mode
        if self.tree is not None:
            self.tree.destroy()
        for w in self.buttons.winfo_children():
            w.destroy()
        if mode == "complaints":
            self.tree = build_table(self.panel, ("id", "student", "category", "status", "assigned", "created"),
                                    ("ID", "Student", "Category", "Status", "Assigned To", "Created"),
                                    (45, 150, 100, 90, 130, 140), height=10)
            ttk.Button(self.buttons, text="Take It", style="Secondary.TButton",
                       command=self.on_take).pack(side="left", padx=(0, 8))
            ttk.Button(self.buttons, text="Resolve", style="Primary.TButton", command=self.on_resolve).pack(side="left")
        else:
            self.tree = build_table(self.panel, ("student", "room"), ("Student out of the hostel", "Room"),
                                    (260, 100), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.buttons.pack_forget()
        if mode == "complaints":
            self.buttons.pack(anchor="e", pady=(10, 0))

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("No Selection", "Select a complaint first.")
            return None
        return self.tree.item(sel[0])["values"]

    def on_take(self):
        vals = self._selected()
        if vals is None:
            return
        try:
            complaint_service.take_complaint(vals[0])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Complaint", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "take_complaint_ui", e)

    def on_serve(self):
        sel = self.qtree.selection()
        if not sel:
            messagebox.showerror("No Selection", "Select a student first.")
            return
        try:
            mess_service.serve(self.qtree.item(sel[0])["values"][0])
            self._rebuild_queue()
        except ValidationError as e:
            messagebox.showerror("Mess queue", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "serve_ui", e)

    def on_serve_next(self):
        first = self.qtree.get_children()
        if not first:
            messagebox.showinfo("Mess queue", "Nobody is waiting.")
            return
        try:
            mess_service.serve(self.qtree.item(first[0])["values"][0])
            self._rebuild_queue()
        except ValidationError as e:
            messagebox.showerror("Mess queue", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "serve_next_ui", e)

    def on_clear(self):
        if not messagebox.askyesno("Clear queue", "Remove everyone still waiting?", parent=self):
            return
        try:
            mess_service.clear_queue()
            self._rebuild_queue()
        except ValidationError as e:
            messagebox.showerror("Mess queue", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "clear_queue_ui", e)

    def _rebuild_queue(self):
        for row in self.qtree.get_children():
            self.qtree.delete(row)
        for r in mess_service.get_queue():
            self.qtree.insert("", "end", values=(r["queue_id"], r["student_name"], r["room_number"] or "-", r["meal"], r["joined_at"]),
                              tags=("default",))

    def on_resolve(self):
        vals = self._selected()
        if vals is None:
            return
        notes = simpledialog.askstring("Resolve", "What was done?", parent=self)
        if notes is None:
            return
        try:
            complaint_service.resolve_complaint(vals[0], notes)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Complaint", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "resolve_complaint_ui", e)

    def refresh(self):
        role = session.get_role()
        if role not in session.SPECIALIST_ROLES:
            return
        for w in self.kpis.winfo_children():
            w.destroy()
        colours = {"orange": (COLORS["orange"], COLORS["orange_soft"]), "info": (COLORS["info"], COLORS["info_soft"]),
                   "success": (COLORS["success"], COLORS["success_soft"]), "pink": (COLORS["pink"], COLORS["pink_soft"]),
                   "accent": (COLORS["accent"], COLORS["accent_soft"])}
        items = [(label, str(value), icon, *colours[c]) for label, value, icon, c in duty_service.summary()]
        kpi_row(self.kpis, items, self.fonts).pack(fill="x")
        if role == "Security Staff":
            self._build_table("out")
            for row in self.tree.get_children():
                self.tree.delete(row)
            for s in gate_service.students_for_gate():
                if s["is_out"]:
                    self.tree.insert("", "end", values=(s["student_name"], s["room_number"]), tags=("default",))
        else:
            self._build_table("complaints")
            self._rows = {}
            keep_selection(self.tree, self._rebuild)
        if role == "Mess Staff":
            self.qpanel.master.pack(fill="both", expand=True, pady=(12, 0))
            self._rebuild_queue()
        else:
            self.qpanel.master.pack_forget()

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in complaint_service.get_my_queue():
            item = self.tree.insert("", "end", values=(c["complaint_id"], c["student_name"], c["category"], c["status"],
                                                       c["assigned_to"] or "-", c["created_at"]),
                                    tags=(status_tag(c["status"]),))
            self._rows[item] = c
