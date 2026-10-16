"""Student sign-up dialog, opened from the login screen. Accounts stay pending until an Administrator approves."""
import tkinter as tk
from tkinter import ttk

from app.config import APP_NAME
from app.services import auth_service
from app.theme import COLORS
from app.utils.validation import ValidationError


class SignupDialog(tk.Toplevel):
    def __init__(self, master, fonts):
        super().__init__(master)
        self.fonts = fonts
        self.title(f"{APP_NAME} — Student Sign Up")
        self.configure(bg=COLORS["surface"])
        self.resizable(False, False)
        width, height = 420, 590
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        wrapper = tk.Frame(self, bg=COLORS["surface"])
        wrapper.pack(fill="both", expand=True, padx=36, pady=30)
        tk.Label(wrapper, text="Create your account", bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["header"]).pack(anchor="w")
        tk.Label(wrapper, text="Use the registration and contact number the hostel has on record.\n"
                                "An administrator must approve your account before you can log in.",
                  bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"], justify="left",
                  wraplength=340).pack(anchor="w", pady=(2, 16))

        self.vars = {key: tk.StringVar() for key in ("reg", "contact", "username", "password", "confirm")}
        self.entries = []
        for key, label, secret in (("reg", "Registration No.", False), ("contact", "Contact No.", False),
                                    ("username", "Choose a username", False), ("password", "Choose a password", True),
                                    ("confirm", "Repeat password", True)):
            tk.Label(wrapper, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                      font=fonts["label"]).pack(anchor="w")
            entry = ttk.Entry(wrapper, textvariable=self.vars[key], show="•" if secret else "")
            entry.pack(fill="x", pady=(3, 10))
            self.entries.append(entry)

        self.message = tk.Label(wrapper, text="", bg=COLORS["surface"], fg=COLORS["danger"],
                                 font=fonts["label"], wraplength=340, justify="left")
        self.message.pack(anchor="w", pady=(0, 6))
        buttons = tk.Frame(wrapper, bg=COLORS["surface"])
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Request Account", style="Primary.TButton",
                    command=self.on_submit).pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Cancel", style="Secondary.TButton",
                    command=self.close).pack(side="left", padx=(8, 0))

        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.grab_set()
        self.entries[0].focus_set()

    def close(self):
        self.grab_release()
        self.destroy()

    def on_submit(self):
        if self.vars["password"].get() != self.vars["confirm"].get():
            self.message.configure(text="The two passwords do not match.", fg=COLORS["danger"])
            return
        try:
            auth_service.register_student(self.vars["username"].get(), self.vars["password"].get(),
                                           self.vars["reg"].get(), self.vars["contact"].get())
        except ValidationError as e:
            self.message.configure(text=str(e), fg=COLORS["danger"])
            return
        for entry in self.entries:
            entry.configure(state="disabled")
        self.message.configure(text="Request sent. You can log in once an administrator approves your account.",
                                fg=COLORS["success"])
