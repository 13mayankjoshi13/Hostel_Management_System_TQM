"""
Splash screen — new in Batch 5.

Shown for a short, fixed duration when the app launches, before the
main window (Dashboard) appears. Purely cosmetic (no data loading
actually depends on it — the database is already initialized by the
time this shows), but it's a standard "app-like" touch that sets the
tone before the Dashboard hub appears.
"""
import tkinter as tk
from tkinter import ttk

from app.theme import COLORS
from app.config import APP_NAME


class SplashScreen(tk.Toplevel):
    def __init__(self, master, fonts, on_finish, duration_ms: int = 1600):
        super().__init__(master)
        self._on_finish = on_finish

        self.overrideredirect(True)   # borderless
        self.configure(bg=COLORS["background"])

        width, height = 520, 300
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Thin accent border to keep the borderless window from feeling
        # like it's floating with no edge at all.
        self.configure(highlightthickness=1, highlightbackground=COLORS["primary"])

        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)

        tk.Label(wrapper, text="🏨", bg=COLORS["background"], fg=COLORS["primary"],
                  font=("Segoe UI", 40)).pack(pady=(48, 8))
        tk.Label(wrapper, text=APP_NAME, bg=COLORS["background"], fg=COLORS["text_light"],
                  font=fonts["splash_title"]).pack()
        tk.Label(wrapper, text="Quality-first hostel administration • TQM Q09",
                  bg=COLORS["background"], fg=COLORS["text_muted"],
                  font=fonts["splash_tagline"]).pack(pady=(4, 28))

        progress = ttk.Progressbar(wrapper, mode="indeterminate", length=260)
        progress.pack()
        progress.start(12)

        self.after(duration_ms, self._finish)

    def _finish(self):
        self.destroy()
        self._on_finish()
