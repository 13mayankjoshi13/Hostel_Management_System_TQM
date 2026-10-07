"""
Login screen (Batch 9). A modal Toplevel shown after the splash and
before the main window's content — the app stays withdrawn until
authenticate() succeeds.
"""
import tkinter as tk
from tkinter import ttk

from app.theme import COLORS
from app.config import APP_NAME
from app.services import auth_service
from app.utils.validation import ValidationError


class LoginScreen(tk.Toplevel):
    def __init__(self, master, fonts, on_success):
        super().__init__(master)
        self.fonts = fonts
        self._on_success = on_success

        self.title(f"{APP_NAME} — Log In")
        self.configure(bg=COLORS["surface"])
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # must log in to proceed

        width, height = 440, 380
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        wrapper = tk.Frame(self, bg=COLORS["surface"])
        wrapper.pack(fill="both", expand=True, padx=32, pady=28)

        tk.Label(wrapper, text=APP_NAME, bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["splash_title"]).pack(anchor="w")
        tk.Label(wrapper, text="Sign in to continue.", bg=COLORS["surface"],
                  fg=COLORS["text_secondary"], font=fonts["subheader"]).pack(anchor="w", pady=(2, 20))

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(wrapper, text="Username", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["label"]).pack(anchor="w")
        username_entry = ttk.Entry(wrapper, textvariable=self.username_var)
        username_entry.pack(fill="x", pady=(2, 12))

        tk.Label(wrapper, text="Password", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["label"]).pack(anchor="w")
        password_entry = ttk.Entry(wrapper, textvariable=self.password_var, show="•")
        password_entry.pack(fill="x", pady=(2, 8))

        self.error_label = tk.Label(wrapper, text="", bg=COLORS["surface"], fg=COLORS["danger"],
                                      font=fonts["label"], wraplength=376, justify="left")
        self.error_label.pack(anchor="w", pady=(0, 8))

        ttk.Button(wrapper, text="Log In", style="Primary.TButton",
                    command=self.on_login).pack(anchor="w", pady=(4, 0))

        tk.Label(wrapper, text="First run default: admin / admin123",
                  bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=fonts["label"]).pack(
            anchor="w", pady=(16, 0))

        username_entry.bind("<Return>", lambda e: password_entry.focus_set())
        password_entry.bind("<Return>", lambda e: self.on_login())
        self.grab_set()
        username_entry.focus_set()

    def on_login(self):
        try:
            user = auth_service.authenticate(self.username_var.get(), self.password_var.get())
            self.grab_release()
            self.destroy()
            self._on_success(user)
        except ValidationError as e:
            self.error_label.configure(text=str(e))
            self.password_var.set("")
