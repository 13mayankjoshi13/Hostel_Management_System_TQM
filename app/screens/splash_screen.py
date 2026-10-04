"""
Splash screen — brief, plain, shown on launch before the Dashboard.
Kept minimal: wordmark, one line of context, thin progress bar.
"""
import tkinter as tk
from tkinter import ttk

from app.theme import COLORS
from app.config import APP_NAME


class SplashScreen(tk.Toplevel):
    def __init__(self, master, fonts, on_finish, duration_ms: int = 1100):
        super().__init__(master)
        self._on_finish = on_finish

        self.overrideredirect(True)
        self.configure(bg=COLORS["surface"], highlightthickness=1,
                        highlightbackground=COLORS["border"])

        width, height = 420, 220
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        wrapper = tk.Frame(self, bg=COLORS["surface"])
        wrapper.pack(fill="both", expand=True, padx=36, pady=36)

        tk.Label(wrapper, text=APP_NAME, bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["splash_title"]).pack(anchor="w", pady=(16, 4))
        tk.Label(wrapper, text="Quality-first hostel administration",
                  bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["splash_tagline"]).pack(anchor="w", pady=(0, 28))

        progress = ttk.Progressbar(wrapper, mode="indeterminate", length=340)
        progress.pack(anchor="w")
        progress.start(10)

        self.after(duration_ms, self._finish)

    def _finish(self):
        self.destroy()
        self._on_finish()
