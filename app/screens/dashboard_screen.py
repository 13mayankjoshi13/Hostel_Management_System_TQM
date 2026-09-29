"""
Dashboard screen — new in Batch 4.

The landing screen when the app opens. Shows live counts pulled straight
from the service layer (never fabricated/hard-coded), plus a "Recent
Activity" panel reading the tail of TQM/data/audit_logs.csv — a direct,
visible link between the software and the TQM evidence it's supposed to
be generating, which is worth showing off in the demo.

If audit_logs.csv doesn't exist yet (fresh install, nothing done in the
app yet), the panel shows an empty-state message instead of erroring.
"""
import csv
import os
import tkinter as tk
from tkinter import ttk

from app.services import student_service, room_service, allocation_service, complaint_service
from app.config import AUDIT_LOG_CSV
from app.theme import COLORS, build_card, build_stat_card, style_treeview_stripes, stripe_tag


class DashboardScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._build_header()
        self._build_stats_row()
        self._build_activity_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=16)
        tk.Label(inner, text="Dashboard", bg=COLORS["header_bg"],
                  fg=COLORS["text_dark"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Live snapshot of hostel operations.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_stats_row(self):
        self.stats_wrapper = tk.Frame(self, bg=COLORS["background"])
        self.stats_wrapper.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(4):
            self.stats_wrapper.columnconfigure(i, weight=1, uniform="stats")
        self.stat_cards = {}

    def _build_activity_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(16, 24))
        content = build_card(wrapper, "Recent Activity (from TQM/data/audit_logs.csv)",
                              self.fonts, accent=COLORS["accent_blue"])

        columns = ("timestamp", "module", "action", "description")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        for col, label, width in zip(columns, ("Timestamp", "Module", "Action", "Description"),
                                       (150, 110, 90, 380)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_stripes(self.tree)

        self.empty_label = tk.Label(
            content, text="No activity recorded yet — add a student, room, or "
                          "allocation to see real audit evidence appear here.",
            bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=self.fonts["body"],
        )

    def _refresh_stats(self):
        for widget in self.stats_wrapper.winfo_children():
            widget.destroy()

        students = student_service.get_all_students()
        rooms = room_service.get_all_rooms()
        active_allocations = allocation_service.get_active_allocations()
        complaints = complaint_service.get_all_complaints()

        total_capacity = sum(r["capacity"] for r in rooms)
        occupancy_pct = (
            round(len(active_allocations) / total_capacity * 100)
            if total_capacity > 0 else 0
        )
        open_complaints = sum(1 for c in complaints if c["status"] == "Open")

        tiles = [
            ("Total Students", str(len(students)), COLORS["primary"]),
            ("Rooms Occupied", f"{occupancy_pct}%", COLORS["accent_blue"]),
            ("Active Allocations", str(len(active_allocations)), COLORS["success"]),
            ("Open Complaints", str(open_complaints), COLORS["accent_amber"]),
        ]
        for i, (label, value, accent) in enumerate(tiles):
            card = build_stat_card(self.stats_wrapper, label, value, accent, self.fonts)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

    def _refresh_activity(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self._read_recent_audit_entries(limit=8)
        if not rows:
            self.tree.pack_forget()
            self.empty_label.pack(fill="x", pady=8)
            return

        self.empty_label.pack_forget()
        self.tree.pack(fill="both", expand=True)
        for i, entry in enumerate(rows):
            self.tree.insert("", "end", values=(
                entry.get("timestamp", ""), entry.get("module", ""),
                entry.get("action", ""), entry.get("description", ""),
            ), tags=(stripe_tag(i),))

    @staticmethod
    def _read_recent_audit_entries(limit=8):
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
