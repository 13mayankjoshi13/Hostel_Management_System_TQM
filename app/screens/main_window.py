"""
Application shell — Batch 4 redesign.

Batch 3 used a dark LEFT SIDEBAR for navigation. This version uses a
dark TOP NAVBAR with pill-style nav buttons instead, and adds a
Dashboard as the landing screen. This is a deliberate layout change
(not just a recolor) since the previous look had been copied by other
students and needed to look distinctly different for the demo.

Each screen (DashboardScreen, StudentScreen, RoomScreen,
AllocationScreen, ComplaintScreen) is fully self-contained in
app/screens/ — this file only wires navigation.
"""
import tkinter as tk

from app.config import APP_NAME
from app.theme import COLORS, apply_theme
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
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1080x640")
        self.minsize(920, 580)

        self.fonts = apply_theme(self)
        self._nav_buttons = {}
        self.screens = {}

        self._build_navbar()

        self.content = tk.Frame(self, bg=COLORS["background"])
        self.content.pack(side="top", fill="both", expand=True)

        self._create_screens()
        self.show_screen("Dashboard")

    def _build_navbar(self):
        navbar = tk.Frame(self, bg=COLORS["navbar_bg"], height=56)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        brand = tk.Frame(navbar, bg=COLORS["navbar_bg"])
        brand.pack(side="left", padx=20)
        tk.Label(brand, text="🏨 Hostel MS", bg=COLORS["navbar_bg"],
                  fg=COLORS["navbar_text_active"], font=self.fonts["brand"]).pack()

        tk.Frame(navbar, bg="#1E293B", width=1).pack(side="left", fill="y", pady=12)

        nav_area = tk.Frame(navbar, bg=COLORS["navbar_bg"])
        nav_area.pack(side="left", padx=8)

        for key, label in _NAV_ITEMS:
            pill = tk.Frame(nav_area, bg=COLORS["navbar_bg"])
            pill.pack(side="left", padx=4, pady=10)
            btn = tk.Button(
                pill, text=label, bd=0, padx=16, pady=8,
                bg=COLORS["navbar_bg"], fg=COLORS["navbar_text"],
                activebackground=COLORS["navbar_pill_active"],
                activeforeground=COLORS["navbar_text_active"],
                font=self.fonts["nav"], relief="flat", cursor="hand2",
                command=lambda k=key: self.show_screen(k),
            )
            btn.pack()
            self._nav_buttons[key] = btn

        role_area = tk.Frame(navbar, bg=COLORS["navbar_bg"])
        role_area.pack(side="right", padx=20)
        tk.Label(role_area, text="Administrator", bg=COLORS["navbar_bg"],
                  fg=COLORS["navbar_text"], font=self.fonts["subheader"]).pack()

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
        for nav_key, btn in self._nav_buttons.items():
            active = nav_key == key
            btn.configure(
                bg=COLORS["navbar_pill_active"] if active else COLORS["navbar_bg"],
                fg=COLORS["navbar_text_active"] if active else COLORS["navbar_text"],
            )
