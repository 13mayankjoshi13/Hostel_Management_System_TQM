"""
Dashboard: greeting banner, KPI cards, rooms overview and recent
activity on the right; calendar and quick actions on the left.
"""
import csv
import os
import tkinter as tk
from datetime import date, datetime

from app.config import AUDIT_LOG_CSV
from app.screens.calendar_widget import CalendarWidget, UpcomingList
from app.services import (event_service, student_service, room_service, allocation_service, complaint_service,
                           bug_service, leave_service)
from app.theme import (COLORS, Card, ScrollFrame, _round_rect, build_table, chip, icon_tile,
                        kpi_row, style_treeview_status_tags)
from app.utils import session


def _greeting() -> str:
    hour = datetime.now().hour
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"


class DashboardScreen(tk.Frame):
    def __init__(self, parent, fonts, navigate=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._navigate = navigate or (lambda key: None)
        self._tab = "rooms"

        self.columnconfigure(0, weight=0, minsize=312)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=COLORS["background"])
        left.grid(row=0, column=0, sticky="ns", padx=(24, 10), pady=(8, 20))
        right = tk.Frame(self, bg=COLORS["background"])
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 24), pady=(8, 20))

        self._build_left(left)
        self._build_right(right)
        self.refresh()

    # ------------------------------------------------------------ left
    def _build_left(self, left):
        cal_card = Card(left, fit=True)
        cal_card.pack(fill="x")
        self.calendar = CalendarWidget(cal_card.body, self.fonts)
        self.calendar.pack(fill="x")

        actions = Card(left, fit=True)
        actions.pack(fill="x", pady=(14, 0))
        tk.Label(actions.body, text="QUICK ACTIONS", bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                  font=self.fonts["small_bold"]).pack(anchor="w", pady=(0, 8))
        grid = tk.Frame(actions.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        tiles = [("Add student", "user", COLORS["accent"], "Students"),
                 ("Allocate room", "key", COLORS["teal"], "Allocation"),
                 ("Log complaint", "chat", COLORS["pink"], "Complaints"),
                 ("Record leave", "plane", COLORS["orange"], "Leaves")]
        for i, (label, icon, color, target) in enumerate(tiles):
            grid.columnconfigure(i, weight=1)
            cell = tk.Frame(grid, bg=COLORS["surface"], cursor="hand2")
            cell.grid(row=0, column=i, sticky="n")
            tile = icon_tile(cell, icon, color, size=46, bg=COLORS["surface"])
            tile.pack()
            text = tk.Label(cell, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                             font=self.fonts["small"], wraplength=64, justify="center")
            text.pack(pady=(5, 0))
            for w in (cell, tile, text):
                w.bind("<Button-1>", lambda e, t=target: self._navigate(t))

        upcoming = Card(left, fit=True)
        upcoming.pack(fill="x", pady=(14, 0))
        tk.Label(upcoming.body, text="UPCOMING", bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                  font=self.fonts["small_bold"]).pack(anchor="w", pady=(0, 6))
        self.upcoming = UpcomingList(upcoming.body, self.fonts, limit=3)
        self.upcoming.pack(fill="x")

    # ------------------------------------------------------------ right
    def _build_right(self, right):
        self.banner = tk.Canvas(right, height=118, bg=COLORS["background"], highlightthickness=0, bd=0)
        self.banner.pack(fill="x")
        self.banner.bind("<Configure>", lambda e: self._draw_banner())
        self._banner_text = ("", "")

        self.kpi_slot = tk.Frame(right, bg=COLORS["background"])
        self.kpi_slot.pack(fill="x", pady=(14, 14))

        panel = Card(right, fit=False)
        panel.pack(fill="both", expand=True)
        head = tk.Frame(panel.body, bg=COLORS["surface"])
        head.pack(fill="x", pady=(0, 10))
        self.tab_labels = {}
        for key, text in (("rooms", "Rooms"), ("activity", "Recent activity")):
            lbl = tk.Label(head, text=text, bg=COLORS["surface"], font=self.fonts["section_title"],
                            padx=12, pady=5, cursor="hand2")
            lbl.pack(side="left", padx=(0, 6))
            lbl.bind("<Button-1>", lambda e, k=key: self._set_tab(k))
            self.tab_labels[key] = lbl
        self.legend = tk.Frame(head, bg=COLORS["surface"])
        self.legend.pack(side="right")
        for text, fg, bg in (("Vacant", COLORS["success"], COLORS["success_soft"]),
                              ("Partly full", COLORS["warning"], COLORS["warning_soft"]),
                              ("Full", COLORS["accent"], COLORS["accent_soft"])):
            chip(self.legend, text, fg, bg).pack(side="left", padx=3)

        self.body = tk.Frame(panel.body, bg=COLORS["surface"])
        self.body.pack(fill="both", expand=True)

        self.rooms_scroll = ScrollFrame(self.body)
        self.activity_wrap = tk.Frame(self.body, bg=COLORS["surface"])
        self.tree = build_table(self.activity_wrap, ("timestamp", "module", "action", "description"),
                                  ("Time", "Module", "Action", "Description"),
                                  (140, 100, 90, 360), height=9)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.empty_label = tk.Label(self.activity_wrap, text="No activity recorded yet.",
                                      bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=self.fonts["body"])
        self._set_tab("rooms")

    def _set_tab(self, key):
        self._tab = key
        for k, lbl in self.tab_labels.items():
            active = k == key
            lbl.configure(bg=COLORS["accent_soft"] if active else COLORS["surface"],
                          fg=COLORS["accent"] if active else COLORS["text_secondary"])
        self.rooms_scroll.pack_forget()
        self.activity_wrap.pack_forget()
        if key == "rooms":
            self.rooms_scroll.pack(fill="both", expand=True)
            self.legend.pack(side="right")
        else:
            self.activity_wrap.pack(fill="both", expand=True)
            self.legend.pack_forget()

    def _draw_banner(self):
        c = self.banner
        w = max(c.winfo_width(), 200)
        h = 118
        c.delete("all")
        _round_rect(c, 1, 1, w - 2, h - 2, 18, fill=COLORS["hero"], outline="")
        for cx, cy, r, col in ((w - 95, 59, 44, COLORS["hero_alt"]), (w - 175, 78, 26, COLORS["hero_alt2"]),
                                (w - 45, 28, 18, COLORS["hero_alt2"])):
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="")
        title, sub = self._banner_text
        c.create_text(26, 40, anchor="w", text=title, fill="#FFFFFF", font=self.fonts["hero"])
        c.create_text(26, 72, anchor="w", text=sub, fill="#CFCDF5", font=self.fonts["body"])
        c.create_text(26, 96, anchor="w", text=date.today().strftime("%A, %d %B %Y"),
                      fill="#A7A3E8", font=self.fonts["label"])

    # ------------------------------------------------------------ data
    def _refresh_banner_and_kpis(self):
        students = student_service.get_all_students()
        rooms = room_service.get_all_rooms()
        allocations = allocation_service.get_active_allocations()
        complaints = complaint_service.get_all_complaints()
        bugs = bug_service.get_all_bugs()
        on_leave = sum(1 for l in leave_service.get_all_leaves() if l["status"] == "On Leave")

        capacity = sum(r["capacity"] for r in rooms)
        occupancy = round(len(allocations) / capacity * 100) if capacity else 0
        open_complaints = sum(1 for c in complaints if c["status"] == "Open")
        open_bugs = sum(1 for b in bugs if b["status"] in ("Open", "In Progress"))

        name = session.get_user().replace("_", " ").title()
        self._banner_text = (f"{_greeting()}, {name}",
                             f"{len(students)} students · {len(rooms)} rooms · {occupancy}% of beds occupied")
        self._draw_banner()

        for w in self.kpi_slot.winfo_children():
            w.destroy()
        kpi_row(self.kpi_slot, [
            ("Students", str(len(students)), "users", COLORS["accent"], COLORS["accent_soft"]),
            ("Beds occupied", f"{occupancy}%", "door", COLORS["teal"], COLORS["teal_soft"]),
            ("Open complaints", str(open_complaints), "chat", COLORS["orange"], COLORS["orange_soft"]),
            ("On leave now", str(on_leave), "plane", COLORS["info"], COLORS["info_soft"]),
            ("Open bugs", str(open_bugs), "bug", COLORS["pink"], COLORS["pink_soft"]),
        ], self.fonts).pack(fill="x")

        self._rooms = rooms
        self._occupied = {}
        for a in allocations:
            self._occupied[a["room_id"]] = self._occupied.get(a["room_id"], 0) + 1

    def _refresh_rooms(self):
        inner = self.rooms_scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        if not self._rooms:
            tk.Label(inner, text="No rooms yet. Add rooms in the Rooms screen.", bg=COLORS["surface"],
                      fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(pady=20)
            return
        blocks = {}
        for room in sorted(self._rooms, key=lambda r: r["room_number"]):
            blocks.setdefault(room["room_number"][:1].upper(), []).append(room)
        columns = 4
        for block, rooms in blocks.items():
            tk.Label(inner, text=f"BLOCK {block}", bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                      font=self.fonts["small_bold"]).pack(anchor="w", pady=(4, 6))
            grid = tk.Frame(inner, bg=COLORS["surface"])
            grid.pack(fill="x", pady=(0, 8))
            for col in range(columns):
                grid.columnconfigure(col, weight=1, uniform="room")
            for i, room in enumerate(rooms):
                taken = self._occupied.get(room["room_id"], 0)
                if taken == 0:
                    fg, soft, label = COLORS["success"], COLORS["success_soft"], "Vacant"
                elif taken >= room["capacity"]:
                    fg, soft, label = COLORS["accent"], COLORS["accent_soft"], "Full"
                else:
                    fg, soft, label = COLORS["warning"], COLORS["warning_soft"], "Partly full"
                cell = tk.Frame(grid, bg=soft, cursor="hand2", padx=10, pady=8)
                cell.grid(row=i // columns, column=i % columns, sticky="ew", padx=4, pady=4)
                tk.Label(cell, text=room["room_number"], bg=soft, fg=COLORS["text_primary"],
                          font=self.fonts["body_bold"]).pack(anchor="w")
                tk.Label(cell, text=f"{taken}/{room['capacity']} beds · {room['room_type']}", bg=soft,
                          fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w")
                tk.Label(cell, text=label, bg=soft, fg=fg, font=self.fonts["small_bold"]).pack(anchor="w", pady=(3, 0))
                for w in [cell] + list(cell.winfo_children()):
                    w.bind("<Button-1>", lambda e: self._navigate("Allocation"))

    def _refresh_activity(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self._read_recent_audit_entries(limit=9)
        if not rows:
            self.tree.pack_forget()
            self.empty_label.pack(fill="x", pady=8)
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
        self._refresh_banner_and_kpis()
        self._refresh_rooms()
        self._refresh_activity()
        self.calendar.refresh()
        self.upcoming.refresh()
