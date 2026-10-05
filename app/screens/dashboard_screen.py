"""
Dashboard screen — overview only. Navigation is handled by the sidebar
now (see main_window.py), so this screen's only job is a quick read of
where things stand: a KPI strip and the tail of the real audit log.
"""
import csv
import os
import tkinter as tk
from tkinter import ttk

from app.services import student_service, room_service, allocation_service, complaint_service, bug_service
from app.config import AUDIT_LOG_CSV
from app.theme import COLORS, section_header, build_panel, build_stat_row, build_table, style_treeview_status_tags



class DashboardScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Dashboard", "Overview of current hostel operations.", fonts)

        self.stats_slot = tk.Frame(self, bg=COLORS["background"])
        self.stats_slot.pack(fill="x", padx=28, pady=(0, 20))

        table_wrapper = tk.Frame(self, bg=COLORS["background"])
        table_wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(table_wrapper, "Recent Activity", fonts)

        self.tree = build_table(content, ("timestamp", "module", "action", "description"),
                                  ("Timestamp", "Module", "Action", "Description"),
                                  (150, 110, 90, 400), height=9)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        self.empty_label = tk.Label(
            content, text="No activity recorded yet.",
            bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=fonts["body"],
        )

        self.refresh()

    def _refresh_stats(self):
        for w in self.stats_slot.winfo_children():
            w.destroy()

        students = student_service.get_all_students()
        rooms = room_service.get_all_rooms()
        active_allocations = allocation_service.get_active_allocations()
        complaints = complaint_service.get_all_complaints()

        total_capacity = sum(r["capacity"] for r in rooms)
        occupancy_pct = (
            round(len(active_allocations) / total_capacity * 100) if total_capacity > 0 else 0
        )
        open_complaints = sum(1 for c in complaints if c["status"] == "Open")
        bugs = bug_service.get_all_bugs()
        open_bugs = sum(1 for b in bugs if b["status"] in ("Open", "In Progress"))

        build_stat_row(self.stats_slot, [
            ("Total Students", str(len(students))),
            ("Rooms Occupied", f"{occupancy_pct}%"),
            ("Active Allocations", str(len(active_allocations))),
            ("Open Complaints", str(open_complaints)),
            ("Open Bugs", str(open_bugs)),
        ], self.fonts)

    def _refresh_activity(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self._read_recent_audit_entries(limit=9)
        if not rows:
            self.tree.pack_forget()
            self.empty_label.pack(fill="x", pady=4)
            return

        self.empty_label.pack_forget()
        self.tree.pack(fill="both", expand=True)
        for entry in rows:
            self.tree.insert("", "end", values=(
                entry.get("timestamp", ""), entry.get("module", ""),
                entry.get("action", ""), entry.get("description", ""),
            ), tags=("default",))

    @staticmethod
    def _read_recent_audit_entries(limit=9):
        if not os.path.exists(AUDIT_LOG_CSV):
            return []
        try:
            with open(AUDIT_LOG_CSV, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            return list(reversed(rows[-limit:]))
        except Exception:
            return []

    def refresh(self):
        self._refresh_stats()
        self._refresh_activity()
