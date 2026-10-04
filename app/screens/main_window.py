"""
Application shell — Batch 6.

Back to a persistent sidebar (the most practical pattern for a tool used
many times a day), but styled plainly: white/near-white background,
thin right border, text-only items, a 3px accent bar + medium-weight
text for the active item, subtle gray hover. No icons, no color fills,
no pill shapes — restrained on purpose.
"""
import tkinter as tk

from app.config import APP_NAME
from app.theme import COLORS, apply_theme, bind_hover
from app.screens.splash_screen import SplashScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.student_screen import StudentScreen
from app.screens.room_screen import RoomScreen
from app.screens.allocation_screen import AllocationScreen
from app.screens.complaint_screen import ComplaintScreen

_NAV_ITEMS = [
    ("Dashboard", "Dashboard"),
    ("Students", "Students"),
    ("Rooms", "Rooms"),
    ("Allocation", "Room Allocation"),
    ("Complaints", "Complaints"),
]


class MainWindow(tk.Tk):
    def __init__(self, show_splash: bool = True):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(960, 620)

        self.fonts = apply_theme(self)
        self.screens = {}
        self._nav_rows = {}

        body = tk.Frame(self, bg=COLORS["background"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        self.content = tk.Frame(body, bg=COLORS["background"])
        self.content.pack(side="left", fill="both", expand=True)

        self._create_screens()

        if show_splash:
            self.withdraw()
            SplashScreen(self, self.fonts, on_finish=self._enter_app)
        else:
            self._enter_app()

    def _enter_app(self):
        self.deiconify()
        self.show_screen("Dashboard")

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS["sidebar_bg"], width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        brand.pack(fill="x", padx=20, pady=(22, 18))
        tk.Label(brand, text="Hostel MS", bg=COLORS["sidebar_bg"], fg=COLORS["text_primary"],
                  font=self.fonts["brand"], justify="left").pack(anchor="w")
        tk.Label(brand, text="Administration", bg=COLORS["sidebar_bg"], fg=COLORS["text_tertiary"],
                  font=self.fonts["subheader"], justify="left").pack(anchor="w", pady=(1, 0))

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x")

        nav_wrap = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        nav_wrap.pack(fill="x", pady=8)

        for key, label in _NAV_ITEMS:
            row = tk.Frame(nav_wrap, bg=COLORS["sidebar_bg"])
            row.pack(fill="x")
            bar = tk.Frame(row, bg=COLORS["sidebar_bg"], width=3)
            bar.pack(side="left", fill="y")
            btn = tk.Label(row, text=label, bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"],
                            font=self.fonts["nav"], anchor="w", padx=17, pady=9, cursor="hand2")
            btn.pack(side="left", fill="x", expand=True)
            btn.bind("<Button-1>", lambda e, k=key: self.show_screen(k))
            bind_hover(btn, COLORS["sidebar_bg"], "#EFEFF1")
            self._nav_rows[key] = (bar, btn)

        tk.Frame(sidebar, bg=COLORS["sidebar_bg"]).pack(fill="both", expand=True)
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x")
        tk.Label(sidebar, text="TQM Q09 — Reduce Bugs", bg=COLORS["sidebar_bg"],
                  fg=COLORS["text_tertiary"], font=self.fonts["subheader"], wraplength=170,
                  justify="left").pack(anchor="w", padx=20, pady=14)

    def _create_screens(self):
        self.screens["Dashboard"] = DashboardScreen(self.content, self.fonts)
        self.screens["Students"] = StudentScreen(self.content, self.fonts)
        self.screens["Rooms"] = RoomScreen(self.content, self.fonts)
        self.screens["Allocation"] = AllocationScreen(self.content, self.fonts)
        self.screens["Complaints"] = ComplaintScreen(self.content, self.fonts)
        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_screen(self, key: str):
        self.screens[key].tkraise()
        self.screens[key].refresh()
        for nav_key, (bar, btn) in self._nav_rows.items():
            active = nav_key == key
            bar.configure(bg=COLORS["accent"] if active else COLORS["sidebar_bg"])
            btn.configure(fg=COLORS["text_primary"] if active else COLORS["text_secondary"],
                          font=self.fonts["nav_active"] if active else self.fonts["nav"])
