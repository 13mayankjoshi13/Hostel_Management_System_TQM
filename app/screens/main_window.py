"""
Application shell — Batch 5 redesign.

Navigation history:
  - Batch 3: dark LEFT SIDEBAR, 5 always-visible nav items, light theme.
  - Batch 4: dark TOP NAVBAR, 5 always-visible nav pills, light theme.
  - Batch 5 (this one): DARK theme throughout, a SPLASH SCREEN on
    launch, then a slim top bar with just the brand + a single Home
    button, and hub-and-spoke navigation — the Dashboard has big
    clickable module tiles, and every other screen has a "🏠 Dashboard"
    breadcrumb to come back. There is no persistent multi-item nav list
    anywhere anymore.

Each screen (DashboardScreen, StudentScreen, RoomScreen,
AllocationScreen, ComplaintScreen) is fully self-contained in
app/screens/ — this file wires navigation and the splash sequence.
"""
import tkinter as tk

from app.config import APP_NAME
from app.theme import COLORS, apply_theme
from app.screens.splash_screen import SplashScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.student_screen import StudentScreen
from app.screens.room_screen import RoomScreen
from app.screens.allocation_screen import AllocationScreen
from app.screens.complaint_screen import ComplaintScreen


class MainWindow(tk.Tk):
    def __init__(self, show_splash: bool = True):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1080x720")
        self.minsize(960, 640)

        self.fonts = apply_theme(self)
        self.screens = {}

        self._build_topbar()
        self.content = tk.Frame(self, bg=COLORS["background"])
        self.content.pack(side="top", fill="both", expand=True)

        self._create_screens()

        if show_splash:
            self.withdraw()
            SplashScreen(self, self.fonts, on_finish=self._enter_app)
        else:
            self._enter_app()

    def _enter_app(self):
        self.deiconify()
        self.show_screen("Dashboard")

    def _build_topbar(self):
        topbar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🏨 Hostel MS", bg=COLORS["topbar_bg"],
                  fg=COLORS["text_light"], font=self.fonts["brand"]).pack(side="left", padx=18)

        self.home_button = tk.Button(
            topbar, text="🏠 Dashboard", bd=0, padx=14, pady=6,
            bg=COLORS["topbar_bg"], fg=COLORS["primary"],
            activebackground=COLORS["surface"], activeforeground=COLORS["primary"],
            font=self.fonts["body_bold"], relief="flat", cursor="hand2",
            command=lambda: self.show_screen("Dashboard"),
        )
        self.home_button.pack(side="right", padx=18)

    def _create_screens(self):
        go_home = lambda: self.show_screen("Dashboard")
        self.screens["Dashboard"] = DashboardScreen(self.content, self.fonts, navigate=self.show_screen)
        self.screens["Students"] = StudentScreen(self.content, self.fonts, go_home=go_home)
        self.screens["Rooms"] = RoomScreen(self.content, self.fonts, go_home=go_home)
        self.screens["Allocation"] = AllocationScreen(self.content, self.fonts, go_home=go_home)
        self.screens["Complaints"] = ComplaintScreen(self.content, self.fonts, go_home=go_home)
        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_screen(self, key: str):
        self.screens[key].tkraise()
        self.screens[key].refresh()
