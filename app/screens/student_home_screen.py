"""Student front page: attendance, fines due, notices, warden, emergency numbers and events."""
import tkinter as tk
from datetime import date, datetime

from app.services import fine_service, home_service
from app.theme import COLORS, Card, ScrollFrame, _round_rect, chip, kpi_row


def _greeting() -> str:
    hour = datetime.now().hour
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"


class StudentHomeScreen(tk.Frame):
    def __init__(self, parent, fonts, navigate=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._navigate = navigate or (lambda key: None)
        self._banner_text = ("", "")
        self.banner = tk.Canvas(self, height=118, bg=COLORS["background"], highlightthickness=0, bd=0)
        self.banner.pack(fill="x", padx=24, pady=(8, 0))
        self.banner.bind("<Configure>", lambda e: self._draw_banner())
        self.scroll = ScrollFrame(self, bg=COLORS["background"])
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(14, 14))

    def _draw_banner(self):
        c = self.banner
        w = max(c.winfo_width(), 200)
        c.delete("all")
        _round_rect(c, 1, 1, w - 2, 116, 18, fill=COLORS["hero"], outline="")
        for cx, cy, r, col in ((w - 95, 59, 44, COLORS["hero_alt"]), (w - 175, 78, 26, COLORS["hero_alt2"]),
                                (w - 45, 28, 18, COLORS["hero_alt2"])):
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="")
        title, sub = self._banner_text
        c.create_text(26, 40, anchor="w", text=title, fill="#FFFFFF", font=self.fonts["hero"])
        c.create_text(26, 72, anchor="w", text=sub, fill="#CFCDF5", font=self.fonts["body"])
        c.create_text(26, 96, anchor="w", text=date.today().strftime("%A, %d %B %Y"),
                      fill="#A7A3E8", font=self.fonts["label"])

    def _card(self, parent, title, row, col, span=1):
        card = Card(parent, fit=True)
        card.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=6, pady=6)
        tk.Label(card.body, text=title, bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                 font=self.fonts["small_bold"]).pack(anchor="w", pady=(0, 6))
        return card.body

    def _line(self, parent, text, font=None, fg=None, wrap=0):
        tk.Label(parent, text=text, bg=COLORS["surface"], fg=fg or COLORS["text_secondary"],
                 font=font or self.fonts["body"], wraplength=wrap, justify="left", anchor="w").pack(anchor="w")

    def refresh(self):
        data = home_service.student_home()
        room = data["room"]
        where = f"Room {room['room_number']} · floor {room['floor']}" if room else "No room allocated yet"
        self._banner_text = (f"{_greeting()}, {data['name'].split()[0]}", where)
        self._draw_banner()

        inner = self.scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        att = data["attendance"]
        due = data["fines_due_paise"]
        kpi_row(inner, [
            ("Present (30 days)", str(att["Present"]), "users", COLORS["success"], COLORS["success_soft"]),
            ("Absent (30 days)", str(att["Absent"]), "chat", COLORS["pink"], COLORS["pink_soft"]),
            ("Leave days (30 days)", str(att["Leave"]), "plane", COLORS["info"], COLORS["info_soft"]),
            ("Fines due", fine_service.format_rupees(due), "clipboard", COLORS["orange"], COLORS["orange_soft"]),
        ], self.fonts).pack(fill="x", pady=(0, 6))

        grid = tk.Frame(inner, bg=COLORS["background"])
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1, uniform="c")
        grid.columnconfigure(1, weight=1, uniform="c")

        body = self._card(grid, "RECENT NOTICES", 0, 0)
        if not data["notices"]:
            self._line(body, "No notices yet.", fg=COLORS["text_tertiary"])
        for n in data["notices"]:
            self._line(body, n["title"], font=self.fonts["body_bold"], fg=COLORS["text_primary"], wrap=330)
            self._line(body, f"{n['created_by']} · {n['created_at']}", font=self.fonts["small"],
                       fg=COLORS["text_tertiary"])
            self._line(body, n["body"][:140] + ("…" if len(n["body"]) > 140 else ""), wrap=330)
            tk.Frame(body, height=6, bg=COLORS["surface"]).pack()

        body = self._card(grid, "MY FINES", 0, 1)
        if not data["fines_due"]:
            self._line(body, "No fines due.", fg=COLORS["success"])
        for f in data["fines_due"]:
            self._line(body, f"{f['amount']} — {f['reason']}", wrap=330)
        if data["fines_due"]:
            tk.Label(body, text="Pay in My Fines", bg=COLORS["surface"], fg=COLORS["accent"], cursor="hand2",
                     font=self.fonts["body_bold"]).pack(anchor="w", pady=(6, 0))
            body.winfo_children()[-1].bind("<Button-1>", lambda e: self._navigate("MyFines"))

        body = self._card(grid, "MY WARDEN", 1, 0)
        w = data["warden"]
        if w:
            self._line(body, w["name"], font=self.fonts["body_bold"], fg=COLORS["text_primary"])
            self._line(body, f"{w['hostel_name']} · {w['contact_number']}")
            if w["office_hours"]:
                self._line(body, f"Office hours: {w['office_hours']}", font=self.fonts["label"])
        else:
            self._line(body, "No warden assigned yet. Ask the hostel office." if data["gender"] else
                       "Your gender is not set yet, so a warden cannot be shown. Ask the hostel office.",
                       fg=COLORS["text_tertiary"], wrap=330)

        body = self._card(grid, "UPCOMING EVENTS", 1, 1)
        if not data["events"]:
            self._line(body, "Nothing coming up.", fg=COLORS["text_tertiary"])
        for e in data["events"]:
            row = tk.Frame(body, bg=COLORS["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=e["event_date"], bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                     font=self.fonts["label"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=e["title"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["body"]).pack(side="left")

        body = self._card(grid, "EMERGENCY NUMBERS", 2, 0, span=2)
        flow = tk.Frame(body, bg=COLORS["surface"])
        flow.pack(fill="x")
        for i, c in enumerate(data["emergency"]):
            cell = tk.Frame(flow, bg=COLORS["accent_soft"], padx=10, pady=6)
            cell.grid(row=i // 4, column=i % 4, sticky="ew", padx=4, pady=4)
            flow.columnconfigure(i % 4, weight=1, uniform="e")
            tk.Label(cell, text=c["number"], bg=COLORS["accent_soft"], fg=COLORS["accent"],
                     font=self.fonts["body_bold"]).pack(anchor="w")
            tk.Label(cell, text=c["name"], bg=COLORS["accent_soft"], fg=COLORS["text_secondary"],
                     font=self.fonts["small"]).pack(anchor="w")
