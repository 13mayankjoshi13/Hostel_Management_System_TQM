"""Month calendar with holidays and events, drawn on a Canvas."""
import calendar
import tkinter as tk
from datetime import date, datetime

from app.services import event_service
from app.theme import COLORS

KIND_COLORS = {"Holiday": COLORS["danger"], "Hostel Event": COLORS["teal"], "Exam": COLORS["orange"]}
_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_ROW_H = 34
_HEAD_H = 26


class CalendarWidget(tk.Frame):
    def __init__(self, parent, fonts, on_select=None, bg=None):
        self._bg = bg or COLORS["surface"]
        super().__init__(parent, bg=self._bg)
        self.fonts = fonts
        self._on_select = on_select
        today = date.today()
        self.year, self.month = today.year, today.month
        self.selected = today
        self._events = {}

        head = tk.Frame(self, bg=self._bg)
        head.pack(fill="x", pady=(0, 6))
        self.title_label = tk.Label(head, text="", bg=self._bg, fg=COLORS["text_primary"],
                                      font=fonts["body_bold"])
        self.title_label.pack(side="left")
        today_btn = tk.Label(head, text="Today", bg=COLORS["accent_soft"], fg=COLORS["accent"],
                              font=fonts["small_bold"], padx=9, pady=3, cursor="hand2")
        today_btn.pack(side="right", padx=(6, 0))
        today_btn.bind("<Button-1>", lambda e: self.go_today())
        for text, delta in (("›", 1), ("‹", -1)):
            btn = tk.Label(head, text=text, bg=self._bg, fg=COLORS["text_secondary"],
                            font=fonts["header"], padx=6, cursor="hand2")
            btn.pack(side="right")
            btn.bind("<Button-1>", lambda e, d=delta: self.shift_month(d))

        self.canvas = tk.Canvas(self, height=_HEAD_H + 5 * _ROW_H, bg=self._bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="x")
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.canvas.bind("<Button-1>", self._on_click)

        legend = tk.Frame(self, bg=self._bg)
        legend.pack(fill="x", pady=(6, 0))
        for kind, color in KIND_COLORS.items():
            dot = tk.Canvas(legend, width=8, height=8, bg=self._bg, highlightthickness=0)
            dot.create_oval(0, 0, 8, 8, fill=color, outline="")
            dot.pack(side="left", padx=(0, 3))
            tk.Label(legend, text=kind, bg=self._bg, fg=COLORS["text_secondary"],
                      font=fonts["small"]).pack(side="left", padx=(0, 10))

        self.day_list = tk.Frame(self, bg=self._bg)
        self.day_list.pack(fill="x", pady=(8, 0))
        self.refresh()

    # -- navigation
    def shift_month(self, delta: int):
        m = self.month + delta
        self.year += (m - 1) // 12
        self.month = (m - 1) % 12 + 1
        self.refresh()

    def go_today(self):
        today = date.today()
        self.year, self.month, self.selected = today.year, today.month, today
        self.refresh()
        if self._on_select:
            self._on_select(self.selected)

    # -- data / drawing
    def refresh(self):
        self.title_label.configure(text=f"{calendar.month_name[self.month]} {self.year}")
        self._events = {}
        for ev in event_service.get_events_for_month(self.year, self.month):
            self._events.setdefault(ev["event_date"], []).append(ev)
        self._draw()
        self._draw_day_list()

    def _cell_geometry(self):
        width = max(self.canvas.winfo_width(), 7 * 30)
        return width / 7.0

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cw = self._cell_geometry()
        for i, name in enumerate(_WEEKDAYS):
            c.create_text(i * cw + cw / 2, _HEAD_H / 2, text=name.upper(),
                          fill=COLORS["text_tertiary"], font=self.fonts["small_bold"])
        today = date.today()
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(self.year, self.month)
        c.configure(height=_HEAD_H + len(weeks) * _ROW_H)
        for r, week in enumerate(weeks):
            for col, day in enumerate(week):
                cx = col * cw + cw / 2
                cy = _HEAD_H + r * _ROW_H + _ROW_H / 2 - 3
                in_month = day.month == self.month
                iso = day.isoformat()
                events = self._events.get(iso, []) if in_month else []
                is_holiday = any(e["kind"] == "Holiday" for e in events)
                if in_month and day == self.selected:
                    c.create_oval(cx - 15, cy - 15, cx + 15, cy + 15, fill=COLORS["accent_soft"], outline="")
                if day == today:
                    c.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, fill=COLORS["accent"], outline="")
                    color = "#FFFFFF"
                elif not in_month:
                    color = COLORS["border_strong"]
                elif is_holiday or col == 6:
                    color = COLORS["danger"]
                else:
                    color = COLORS["text_primary"]
                c.create_text(cx, cy, text=str(day.day), fill=color,
                              font=self.fonts["body_bold"] if (is_holiday or day == today) else self.fonts["body"])
                kinds = []
                for e in events:
                    if e["kind"] not in kinds:
                        kinds.append(e["kind"])
                for k, kind in enumerate(kinds[:3]):
                    dx = (k - (len(kinds[:3]) - 1) / 2.0) * 7
                    c.create_oval(cx + dx - 2, cy + 14, cx + dx + 2, cy + 18,
                                  fill=KIND_COLORS[kind], outline="")

    def _draw_day_list(self):
        for w in self.day_list.winfo_children():
            w.destroy()
        iso = self.selected.isoformat()
        tk.Label(self.day_list, text=self.selected.strftime("%A, %d %B"), bg=self._bg,
                  fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w")
        events = self._events.get(iso, []) if self.selected.month == self.month and self.selected.year == self.year else []
        if not events:
            tk.Label(self.day_list, text="No holiday or event.", bg=self._bg,
                      fg=COLORS["text_tertiary"], font=self.fonts["label"]).pack(anchor="w", pady=(2, 0))
        for ev in events[:3]:
            row = tk.Frame(self.day_list, bg=self._bg)
            row.pack(fill="x", pady=(3, 0))
            dot = tk.Canvas(row, width=8, height=8, bg=self._bg, highlightthickness=0)
            dot.create_oval(0, 0, 8, 8, fill=KIND_COLORS.get(ev["kind"], COLORS["accent"]), outline="")
            dot.pack(side="left", padx=(0, 6))
            tk.Label(row, text=ev["title"], bg=self._bg, fg=COLORS["text_primary"],
                      font=self.fonts["label"], anchor="w").pack(side="left")

    def _on_click(self, event):
        cw = self._cell_geometry()
        col = int(event.x // cw)
        row = int((event.y - _HEAD_H) // _ROW_H)
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(self.year, self.month)
        if 0 <= row < len(weeks) and 0 <= col < 7:
            self.selected = weeks[row][col]
            if self.selected.month != self.month:
                self.year, self.month = self.selected.year, self.selected.month
                self.refresh()
            else:
                self._draw()
                self._draw_day_list()
            if self._on_select:
                self._on_select(self.selected)


class UpcomingList(tk.Frame):
    """Next few holidays/events with a date badge."""

    def __init__(self, parent, fonts, limit=3, bg=None):
        self._bg = bg or COLORS["surface"]
        super().__init__(parent, bg=self._bg)
        self.fonts, self.limit = fonts, limit

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        events = event_service.get_upcoming(date.today().isoformat(), self.limit)
        if not events:
            tk.Label(self, text="Nothing scheduled.", bg=self._bg, fg=COLORS["text_tertiary"],
                      font=self.fonts["label"]).pack(anchor="w")
        for ev in events:
            day = datetime.strptime(ev["event_date"], "%Y-%m-%d")
            color = KIND_COLORS.get(ev["kind"], COLORS["accent"])
            row = tk.Frame(self, bg=self._bg)
            row.pack(fill="x", pady=3)
            badge = tk.Frame(row, bg=COLORS["background"], width=44, height=40)
            badge.pack(side="left")
            badge.pack_propagate(False)
            tk.Label(badge, text=day.strftime("%d"), bg=COLORS["background"], fg=color,
                      font=self.fonts["body_bold"]).pack(pady=(3, 0))
            tk.Label(badge, text=day.strftime("%b").upper(), bg=COLORS["background"],
                      fg=COLORS["text_tertiary"], font=self.fonts["small"]).pack()
            text = tk.Frame(row, bg=self._bg)
            text.pack(side="left", padx=(10, 0))
            tk.Label(text, text=ev["title"], bg=self._bg, fg=COLORS["text_primary"],
                      font=self.fonts["label"]).pack(anchor="w")
            tk.Label(text, text=f"{ev['kind']} · {day.strftime('%a')}", bg=self._bg, fg=color,
                      font=self.fonts["small"]).pack(anchor="w")
