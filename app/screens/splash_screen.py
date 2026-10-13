"""Splash screen: brand panel with a thin progress bar."""
import tkinter as tk
from tkinter import ttk

from app.config import APP_NAME
from app.theme import COLORS, icon_tile


class SplashScreen(tk.Toplevel):
    def __init__(self, master, fonts, on_finish, duration_ms: int = 1300):
        super().__init__(master)
        self._on_finish = on_finish
        self.overrideredirect(True)
        self.configure(bg=COLORS["hero"])

        width, height = 560, 320
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        canvas = tk.Canvas(self, width=width, height=height, bg=COLORS["hero"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        for cx, cy, r, col in ((width - 90, 70, 80, COLORS["hero_alt"]), (width - 200, 250, 48, COLORS["hero_alt2"]),
                                (60, 280, 40, COLORS["hero_alt"]), (width - 40, 215, 22, COLORS["hero_alt2"])):
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="")

        tile = icon_tile(canvas, "home", COLORS["accent"], size=56, bg=COLORS["hero"], radius=16)
        canvas.create_window(48, 70, anchor="nw", window=tile)
        canvas.create_text(48, 160, anchor="w", text=APP_NAME, fill="#FFFFFF", font=fonts["hero"])
        canvas.create_text(48, 192, anchor="w", text="Quality-first hostel administration",
                           fill="#CFCDF5", font=fonts["body"])

        style = ttk.Style(self)
        style.configure("Splash.Horizontal.TProgressbar", troughcolor=COLORS["hero_alt"],
                         background="#FFFFFF", borderwidth=0, thickness=4)
        progress = ttk.Progressbar(canvas, mode="indeterminate", length=300, style="Splash.Horizontal.TProgressbar")
        canvas.create_window(48, 248, anchor="nw", window=progress)
        progress.start(10)

        self.after(duration_ms, self._finish)

    def _finish(self):
        self.destroy()
        self._on_finish()
