"""
Login screen (Batch 9). A modal Toplevel shown after the splash and
before the main window's content — the app stays withdrawn until
authenticate() succeeds.
"""
import tkinter as tk
from tkinter import ttk

from app.screens.signup_screen import SignupDialog
from app.theme import COLORS, icon_tile
from app.config import APP_NAME
from app.services import auth_service
from app.utils.validation import ValidationError

_PANEL_TEXT = {
    "Student": ("Student login", "Sign in to see your room, fines, leave and complaints."),
    "Staff": ("Staff login", "Wardens and staff: sign in to manage your part of the hostel."),
    "Admin": ("Admin login", "Administrators: students, rooms, accounts and reports."),
    "Super Admin": ("Super Admin login", "Full control: settings, quality tools, audit and all accounts."),
}

_TEST_ACCOUNTS = {
    "Student": ("student", "student123", "Demo Student (Mayank Joshi)"),
    "Staff": ("hostel_staff", "staff123", "Demo Staff (also: warden / warden123)"),
    "Admin": ("hostel_admin", "admin123", "Demo Administrator"),
    "Super Admin": ("superadmin", "admin123", "Demo Super Admin (also: admin / admin123)"),
}


class LoginScreen(tk.Toplevel):
    def __init__(self, master, fonts, on_success):
        super().__init__(master)
        self.fonts = fonts
        self._on_success = on_success

        self.title(f"{APP_NAME} — Log In")
        self.configure(bg=COLORS["surface"])
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close_request)

        width, height = 820, 560
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        hero = tk.Canvas(self, width=300, height=height, bg=COLORS["hero"], highlightthickness=0)
        hero.pack(side="left", fill="y")
        for cx, cy, r, col in ((250, 60, 90, COLORS["hero_alt"]), (60, 400, 70, COLORS["hero_alt"]),
                                (230, 370, 36, COLORS["hero_alt2"]), (40, 120, 20, COLORS["hero_alt2"])):
            hero.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="")
        hero.create_window(36, 60, anchor="nw",
                           window=icon_tile(hero, "home", COLORS["accent"], size=52, bg=COLORS["hero"], radius=14))
        hero.create_text(36, 150, anchor="nw", text="Hostel\nManagement\nSystem", fill="#FFFFFF",
                         font=fonts["hero"])
        hero.create_text(36, 250, anchor="nw", text="Rooms, complaints and leaves\nin one place.",
                         fill=COLORS["hero_text"], font=fonts["body"])

        wrapper = tk.Frame(self, bg=COLORS["surface"])
        wrapper.pack(side="left", fill="both", expand=True, padx=40, pady=32)

        self.panel = "Student"
        tabs = tk.Frame(wrapper, bg=COLORS["surface"])
        tabs.pack(fill="x", pady=(0, 12))
        self._tab_labels = {}
        for name in _PANEL_TEXT:
            tab = tk.Label(tabs, text=name, font=fonts["label"], cursor="hand2", padx=9, pady=6)
            tab.pack(side="left", padx=(0, 6))
            tab.bind("<Button-1>", lambda e, n=name: self.select_panel(n))
            self._tab_labels[name] = tab

        self.title_label = tk.Label(wrapper, text="", bg=COLORS["surface"], fg=COLORS["text_primary"],
                                     font=fonts["header"])
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(wrapper, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                                         font=fonts["subheader"], wraplength=380, justify="left")
        self.subtitle_label.pack(anchor="w", pady=(2, 10))

        # Test account quick-fill banner
        self.demo_frame = tk.Frame(wrapper, bg=COLORS["accent_soft"], padx=10, pady=6,
                                   highlightthickness=1, highlightbackground=COLORS["accent"])
        self.demo_frame.pack(fill="x", pady=(0, 12))

        self.demo_lbl = tk.Label(self.demo_frame, text="", bg=COLORS["accent_soft"], fg=COLORS["accent"],
                                 font=fonts["label"], justify="left")
        self.demo_lbl.pack(side="left", fill="x", expand=True)

        demo_btn = ttk.Button(self.demo_frame, text="⚡ Quick Fill", command=self._quick_fill)
        demo_btn.pack(side="right")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(wrapper, text="Username", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["label"]).pack(anchor="w")
        username_entry = ttk.Entry(wrapper, textvariable=self.username_var)
        username_entry.pack(fill="x", pady=(2, 10))

        tk.Label(wrapper, text="Password", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["label"]).pack(anchor="w")
        password_entry = ttk.Entry(wrapper, textvariable=self.password_var, show="•")
        password_entry.pack(fill="x", pady=(2, 6))

        self.error_label = tk.Label(wrapper, text="", bg=COLORS["surface"], fg=COLORS["danger"],
                                      font=fonts["label"], wraplength=380, justify="left")
        self.error_label.pack(anchor="w", pady=(0, 6))

        ttk.Button(wrapper, text="Log In", style="Primary.TButton",
                    command=self.on_login).pack(fill="x", pady=(4, 0))

        self.signup_label = tk.Label(wrapper, text="New student? Create an account", bg=COLORS["surface"],
                                      fg=COLORS["accent"], font=fonts["label"], cursor="hand2")
        self.signup_label.bind("<Button-1>", lambda e: SignupDialog(self, self.fonts))

        self.hint_label = tk.Label(wrapper, text="Default accounts: superadmin / admin123 or admin / admin123",
                                    bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=fonts["label"])

        username_entry.bind("<Return>", lambda e: password_entry.focus_set())
        password_entry.bind("<Return>", lambda e: self.on_login())
        self.select_panel("Student")
        self.grab_set()
        username_entry.focus_set()

    def _quick_fill(self):
        acc = _TEST_ACCOUNTS.get(self.panel)
        if acc:
            self.username_var.set(acc[0])
            self.password_var.set(acc[1])
            self.error_label.configure(text="")

    def select_panel(self, name: str):
        self.panel = name
        title, subtitle = _PANEL_TEXT[name]
        self.title_label.configure(text=title)
        self.subtitle_label.configure(text=subtitle)

        acc = _TEST_ACCOUNTS.get(name)
        if acc:
            self.demo_lbl.configure(text=f"Test Account:  {acc[0]}  /  {acc[1]}  ({acc[2]})")

        for tab_name, tab in self._tab_labels.items():
            active = tab_name == name
            tab.configure(bg=COLORS["accent"] if active else COLORS["background"],
                          fg="#FFFFFF" if active else COLORS["text_secondary"])
        self.signup_label.pack_forget()
        self.hint_label.pack_forget()
        if name == "Student":
            self.signup_label.pack(anchor="w", pady=(10, 0))
        elif name == "Super Admin":
            self.hint_label.pack(anchor="w", pady=(10, 0))
        self.error_label.configure(text="")
        self.password_var.set("")

    def on_close_request(self):
        """Closing the log-in window with the X button quits the application (it cannot run without a login)."""
        self.grab_release()
        self.master.destroy()

    def on_login(self):
        try:
            user = auth_service.authenticate(self.username_var.get(), self.password_var.get(), self.panel)
            self.grab_release()
            self.destroy()
            self._on_success(user)
        except ValidationError as e:
            self.error_label.configure(text=str(e))
            self.password_var.set("")
