"""
Dashboard screen — the hub of the new Batch 5 navigation model.

There is no persistent nav bar/sidebar anymore. Instead:
  - This screen shows live stat tiles + a grid of big "module tiles"
    (Students / Rooms / Room Allocation / Complaints). Clicking a tile
    navigates into that module.
  - Every other screen has a small "🏠 Dashboard" breadcrumb at the top
    (see app.theme.build_breadcrumb) to come back here.

That's the entire navigation system: Dashboard -> module (via tile) and
module -> Dashboard (via breadcrumb). Any screen is reachable from any
other screen by going through the hub.

Also keeps the live stats + "Recent Activity" (from TQM/data/audit_logs.csv)
panel introduced in Batch 4, unchanged in behavior.
"""
import csv
import os
import tkinter as tk
from tkinter import ttk

from app.services import student_service, room_service, allocation_service, complaint_service
from app.config import AUDIT_LOG_CSV
from app.theme import (
    COLORS, build_card, build_stat_card, build_module_tile,
    style_treeview_stripes, stripe_tag,
)

_MODULES = [
    ("Students", "🎓", "Students", "Add and review hosteller records.", "primary"),
    ("Rooms", "🏠", "Rooms", "Manage rooms, types, and capacity.", "accent_violet"),
    ("Allocation", "🔑", "Room Allocation", "Assign and release room allocations.", "success"),
    ("Complaints", "📋", "Complaints", "Log, assign, and resolve complaints.", "accent_amber"),
]


class DashboardScreen(tk.Frame):
    def __init__(self, parent, fonts, navigate):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self.navigate = navigate
        self._build_header()
        self._build_stats_row()
        self._build_module_tiles()
        self._build_activity_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=(20, 16))
        tk.Label(inner, text="Dashboard", bg=COLORS["header_bg"],
                  fg=COLORS["text_light"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Live snapshot of hostel operations. Choose a module below.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_stats_row(self):
        self.stats_wrapper = tk.Frame(self, bg=COLORS["background"])
        self.stats_wrapper.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(4):
            self.stats_wrapper.columnconfigure(i, weight=1, uniform="stats")

    def _build_module_tiles(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(4):
            wrapper.columnconfigure(i, weight=1, uniform="tiles")

        for i, (key, icon, title, subtitle, accent_key) in enumerate(_MODULES):
            tile = build_module_tile(
                wrapper, icon, title, subtitle, COLORS[accent_key],
                command=lambda k=key: self.navigate(k), fonts=self.fonts,
            )
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))

    def _build_activity_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(20, 24))
        content = build_card(wrapper, "Recent Activity (from TQM/data/audit_logs.csv)",
                              self.fonts, accent=COLORS["accent_blue"])

        columns = ("timestamp", "module", "action", "description")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=7)
        for col, label, width in zip(columns, ("Timestamp", "Module", "Action", "Description"),
                                       (150, 110, 90, 380)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_stripes(self.tree)

        self.empty_label = tk.Label(
            content, text="No activity recorded yet — add a student, room, or "
                          "allocation to see real audit evidence appear here.",
            bg=COLORS["surface"], fg=COLORS["text_muted"], font=self.fonts["body"],
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
