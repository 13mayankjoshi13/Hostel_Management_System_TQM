"""
Application shell.

Persistent sidebar (the most practical pattern for a tool used many
times a day), styled plainly: white/near-white background, thin right
border, text-only items, a 3px accent bar + medium-weight text for the
active item, subtle gray hover. No icons, no color fills, no pill
shapes — restrained on purpose.

Batch 9 adds a login gate: splash -> login -> dashboard. The sidebar
footer shows who's logged in and a Log Out link that returns to the
login screen (clearing the session) rather than closing the app.
"""
import tkinter as tk

from app.config import APP_NAME
from app.theme import COLORS, apply_theme, bind_hover
from app.services import auth_service
from app.screens.splash_screen import SplashScreen
from app.screens.login_screen import LoginScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.student_screen import StudentScreen
from app.screens.room_screen import RoomScreen
from app.screens.allocation_screen import AllocationScreen
from app.screens.complaint_screen import ComplaintScreen
from app.screens.bug_screen import BugScreen
from app.screens.quality_screen import QualityScreen

_NAV_ITEMS = [
    ("Dashboard", "Dashboard"),
    ("Students", "Students"),
    ("Rooms", "Rooms"),
    ("Allocation", "Room Allocation"),
    ("Complaints", "Complaints"),
    ("Bugs", "Bug Tracker"),
    ("Quality", "Quality Monitoring"),
]


class MainWindow(tk.Tk):
    def __init__(self, show_splash: bool = True):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1150x820")
        self.minsize(980, 680)

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
            SplashScreen(self, self.fonts, on_finish=self._show_login)
        else:
            self._show_login()

    def _show_login(self):
        LoginScreen(self, self.fonts, on_success=self._enter_app)

    def _enter_app(self, user: dict):
        self._update_account_info(user)
        self.deiconify()
        self.show_screen("Dashboard")

    def _handle_logout(self):
        auth_service.logout()
        self.withdraw()
        self._show_login()

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

        account_area = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        account_area.pack(fill="x", padx=20, pady=(12, 6))
        self.account_label = tk.Label(account_area, text="", bg=COLORS["sidebar_bg"],
                                        fg=COLORS["text_primary"], font=self.fonts["label"],
                                        wraplength=170, justify="left")
        self.account_label.pack(anchor="w")
        logout_link = tk.Label(account_area, text="Log out", bg=COLORS["sidebar_bg"],
                                 fg=COLORS["accent"], font=self.fonts["label"], cursor="hand2")
        logout_link.pack(anchor="w", pady=(2, 0))
        logout_link.bind("<Button-1>", lambda e: self._handle_logout())

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x")
        tk.Label(sidebar, text="TQM Q09 — Reduce Bugs", bg=COLORS["sidebar_bg"],
                  fg=COLORS["text_tertiary"], font=self.fonts["subheader"], wraplength=170,
                  justify="left").pack(anchor="w", padx=20, pady=14)

    def _update_account_info(self, user: dict):
        self.account_label.configure(text=f"{user['username']} · {user['role']}")

    def _create_screens(self):
        self.screens["Dashboard"] = DashboardScreen(self.content, self.fonts)
        self.screens["Students"] = StudentScreen(self.content, self.fonts)
        self.screens["Rooms"] = RoomScreen(self.content, self.fonts)
        self.screens["Allocation"] = AllocationScreen(self.content, self.fonts)
        self.screens["Complaints"] = ComplaintScreen(self.content, self.fonts)
        self.screens["Bugs"] = BugScreen(self.content, self.fonts)
        self.screens["Quality"] = QualityScreen(self.content, self.fonts)
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
