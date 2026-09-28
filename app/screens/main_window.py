"""
Application shell: a colored sidebar for navigation plus a content area
that stacks all four screens and raises the selected one. This replaces
the plain ttk.Notebook tabs used before Batch 3 with a more distinctive,
app-like layout.

Each screen (StudentScreen, RoomScreen, AllocationScreen, ComplaintScreen)
is fully self-contained in app/screens/ — this file only wires navigation.
"""
import tkinter as tk

from app.config import APP_NAME
from app.theme import COLORS, apply_theme
from app.screens.student_screen import StudentScreen
from app.screens.room_screen import RoomScreen
from app.screens.allocation_screen import AllocationScreen
from app.screens.complaint_screen import ComplaintScreen

_NAV_ITEMS = [
    ("Students", "🎓  Students"),
    ("Rooms", "🏠  Rooms"),
    ("Allocation", "🔑  Room Allocation"),
    ("Complaints", "📋  Complaints"),
]


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x620")
        self.minsize(880, 560)

        self.fonts = apply_theme(self)
        self._nav_buttons = {}
        self.screens = {}

        container = tk.Frame(self, bg=COLORS["background"])
        container.pack(fill="both", expand=True)

        self._build_sidebar(container)

        self.content = tk.Frame(container, bg=COLORS["background"])
        self.content.pack(side="left", fill="both", expand=True)

        self._create_screens()
        self.show_screen("Students")

    def _build_sidebar(self, container):
        sidebar = tk.Frame(container, bg=COLORS["sidebar_bg"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title_area = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        title_area.pack(fill="x", pady=(20, 24), padx=18)
        tk.Label(title_area, text="🏨 Hostel MS", bg=COLORS["sidebar_bg"],
                  fg=COLORS["sidebar_text_active"], font=self.fonts["app_title"]).pack(anchor="w")
        tk.Label(title_area, text="Quality-first hostel administration", bg=COLORS["sidebar_bg"],
                  fg=COLORS["sidebar_text"], font=self.fonts["subheader"],
                  wraplength=180, justify="left").pack(anchor="w", pady=(4, 0))

        for key, label in _NAV_ITEMS:
            btn = tk.Button(
                sidebar, text=label, anchor="w", bd=0, padx=18, pady=12,
                bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["sidebar_text_active"],
                font=self.fonts["nav"], relief="flat", cursor="hand2",
                command=lambda k=key: self.show_screen(k),
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        footer = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        footer.pack(side="bottom", fill="x", pady=16, padx=18)
        tk.Label(footer, text="TQM Q09 — Reduce Bugs", bg=COLORS["sidebar_bg"],
                  fg=COLORS["sidebar_text"], font=self.fonts["subheader"]).pack(anchor="w")

    def _create_screens(self):
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
                bg=COLORS["sidebar_hover"] if active else COLORS["sidebar_bg"],
                fg=COLORS["sidebar_text_active"] if active else COLORS["sidebar_text"],
                font=self.fonts["nav_active"] if active else self.fonts["nav"],
            )
