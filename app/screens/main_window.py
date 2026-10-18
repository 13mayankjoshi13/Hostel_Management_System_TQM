"""
Application shell: icon sidebar, top bar (screen name, clock, account),
and the screens. Login gate: splash -> login -> home screen for the role.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

from app.config import APP_NAME
from app.theme import COLORS, apply_theme, draw_icon, icon_tile, initials, _round_rect
from app.services import auth_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error, report_tk_callback_exception
from app.screens.splash_screen import SplashScreen
from app.screens.login_screen import LoginScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.calendar_screen import CalendarScreen
from app.screens.student_screen import StudentScreen
from app.screens.room_screen import RoomScreen
from app.screens.allocation_screen import AllocationScreen
from app.screens.complaint_screen import ComplaintScreen
from app.screens.leave_screen import LeaveScreen
from app.screens.bug_screen import BugScreen
from app.screens.quality_screen import QualityScreen
from app.screens.user_screen import UserScreen
from app.screens.my_room_screen import MyRoomScreen
from app.screens.my_complaints_screen import MyComplaintsScreen
from app.screens.my_leave_screen import MyLeaveScreen
from app.screens.my_details_screen import MyDetailsScreen
from app.utils import session
from app.utils.idle import IdleTracker
from app.utils.logging_service import log_audit
from app.config import IDLE_TIMEOUT_MINUTES

# key, label, icon
_NAV_ITEMS = [
    ("Dashboard", "Dashboard", "grid"),
    ("Calendar", "Calendar", "calendar"),
    ("Students", "Students", "user"),
    ("Rooms", "Rooms", "door"),
    ("Allocation", "Room Allocation", "key"),
    ("Complaints", "Complaints", "chat"),
    ("Leaves", "Leave Tracking", "plane"),
    ("Bugs", "Bug Tracker", "bug"),
    ("Quality", "Quality Monitoring", "chart"),
    ("Users", "User Management", "users"),
    ("MyRoom", "My Room", "home"),
    ("MyComplaints", "My Complaints", "chat"),
    ("MyLeave", "My Leave", "plane"),
    ("MyDetails", "My Details", "user"),
]

_ADMIN_ONLY = {"Users"}
_STUDENT_ONLY = {"MyRoom", "MyComplaints", "MyLeave", "MyDetails"}
_EVERYONE = {"Calendar"}


def _allowed_screens(role: str) -> list:
    keys = [key for key, _, _ in _NAV_ITEMS]
    if role == "Student":
        return [k for k in keys if k in _STUDENT_ONLY] + [k for k in keys if k in _EVERYONE]
    allowed = [k for k in keys if k not in _STUDENT_ONLY]
    if role != "Administrator":
        allowed = [k for k in allowed if k not in _ADMIN_ONLY]
    return allowed


def _home_screen(role: str) -> str:
    return "MyRoom" if role == "Student" else "Dashboard"


class NavItem(tk.Canvas):
    """Sidebar entry: rounded highlight when active, icon + label."""

    def __init__(self, parent, key, label, icon, fonts, on_click):
        super().__init__(parent, height=42, bg=COLORS["sidebar_bg"], highlightthickness=0, bd=0, cursor="hand2")
        self.key, self.label, self.icon, self.fonts = key, label, icon, fonts
        self.active = False
        self.hover = False
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Button-1>", lambda e: on_click(key))
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))

    def _set_hover(self, value):
        self.hover = value
        self._draw()

    def set_active(self, value):
        self.active = value
        self._draw()

    def _draw(self):
        self.delete("all")
        w = max(self.winfo_width(), 60)
        bg = COLORS["accent_soft"] if self.active else COLORS["background"] if self.hover else COLORS["sidebar_bg"]
        if bg != COLORS["sidebar_bg"]:
            _round_rect(self, 0, 2, w - 1, 40, 12, fill=bg, outline="")
        color = COLORS["accent"] if self.active else COLORS["text_tertiary"]
        icon = tk.Canvas(self, width=20, height=20, bg=bg, highlightthickness=0, bd=0)
        draw_icon(icon, self.icon, 20, color)
        icon.bind("<Button-1>", lambda e: self.event_generate("<Button-1>"))
        self.create_window(16, 11, anchor="nw", window=icon)
        self.create_text(48, 21, anchor="w", text=self.label,
                         fill=COLORS["accent"] if self.active else COLORS["text_secondary"],
                         font=self.fonts["nav_active"] if self.active else self.fonts["nav"])


class MainWindow(tk.Tk):
    def __init__(self, show_splash: bool = True):
        super().__init__()
        self.report_callback_exception = report_tk_callback_exception
        self.title(APP_NAME)
        height = min(800, max(self.winfo_screenheight() - 80, 640))
        self.geometry(f"1280x{height}")
        self.minsize(1100, 640)

        self.fonts = apply_theme(self)
        self.screens = {}
        self._nav_items = {}
        self._current = None

        body = tk.Frame(self, bg=COLORS["background"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        main = tk.Frame(body, bg=COLORS["background"])
        main.pack(side="left", fill="both", expand=True)
        self._build_topbar(main)
        self.content = tk.Frame(main, bg=COLORS["background"])
        self.content.pack(fill="both", expand=True)

        self._create_screens()
        self._idle = IdleTracker(IDLE_TIMEOUT_MINUTES * 60)
        for sequence in ("<Motion>", "<Key>", "<Button>", "<MouseWheel>"):
            self.bind_all(sequence, lambda e: self._idle.touch(), add="+")
        self._tick()

        if show_splash:
            self.withdraw()
            SplashScreen(self, self.fonts, on_finish=self._show_login)
        else:
            self._show_login()

    def _show_login(self):
        self._idle.touch()
        LoginScreen(self, self.fonts, on_success=self._enter_app)

    def _force_password_change(self) -> bool:
        prompt = "The default password must be replaced before you continue.\nNew password:"
        while True:
            new_password = simpledialog.askstring("Set a new password", prompt, parent=self, show="•")
            if new_password is None:
                return False
            try:
                auth_service.complete_forced_password_change(new_password)
                messagebox.showinfo("Password changed", "Your password has been updated.", parent=self)
                return True
            except ValidationError as e:
                prompt = f"{e}\nNew password:"

    def _enter_app(self, user: dict):
        if user.get("must_change_password") and not self._force_password_change():
            self._handle_logout()
            return
        self._idle.touch()
        self._update_account_info(user)
        allowed = _allowed_screens(user["role"])
        for item in self._nav_items.values():
            item.pack_forget()
        for key, _, _ in _NAV_ITEMS:
            if key in allowed:
                self._nav_items[key].pack(fill="x", padx=14, pady=1)
        self.deiconify()
        self.show_screen(_home_screen(user["role"]))

    def _change_own_password(self):
        current = simpledialog.askstring("Change password", "Current password:", parent=self, show="•")
        if current is None:
            return
        new = simpledialog.askstring("Change password", "New password:", parent=self, show="•")
        if new is None:
            return
        again = simpledialog.askstring("Change password", "Type the new password again:", parent=self, show="•")
        if again is None:
            return
        try:
            if new != again:
                raise ValidationError("The two new passwords do not match.")
            auth_service.change_own_password(current, new)
            messagebox.showinfo("Password changed", "Your password has been updated.", parent=self)
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)
        except Exception as e:
            handle_unexpected_error("User", "change_own_password_ui", e)

    def _handle_logout(self):
        auth_service.logout()
        self.withdraw()
        self._show_login()

    # ------------------------------------------------------------ chrome
    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS["sidebar_bg"], width=232)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Frame(parent, bg=COLORS["border"], width=1).pack(side="left", fill="y")

        brand = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        brand.pack(fill="x", padx=18, pady=(20, 18))
        icon_tile(brand, "home", COLORS["accent"], size=40, bg=COLORS["sidebar_bg"]).pack(side="left")
        text = tk.Frame(brand, bg=COLORS["sidebar_bg"])
        text.pack(side="left", padx=(10, 0))
        tk.Label(text, text="Hostel MS", bg=COLORS["sidebar_bg"], fg=COLORS["text_primary"],
                  font=self.fonts["brand"]).pack(anchor="w")
        tk.Label(text, text="Management System", bg=COLORS["sidebar_bg"], fg=COLORS["text_tertiary"],
                  font=self.fonts["small"]).pack(anchor="w")

        self.nav_wrap = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        self.nav_wrap.pack(fill="x")
        for key, label, icon in _NAV_ITEMS:
            self._nav_items[key] = NavItem(self.nav_wrap, key, label, icon, self.fonts, self.show_screen)

        tk.Frame(sidebar, bg=COLORS["sidebar_bg"]).pack(fill="both", expand=True)
        footer = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        footer.pack(fill="x", padx=18, pady=(0, 16))
        tk.Frame(footer, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 10))
        change_pw = tk.Label(footer, text="Change password", bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"],
                              font=self.fonts["body"], cursor="hand2")
        change_pw.pack(anchor="w", pady=(0, 8))
        change_pw.bind("<Button-1>", lambda e: self._change_own_password())
        logout = tk.Label(footer, text="Log out", bg=COLORS["sidebar_bg"], fg=COLORS["accent"],
                           font=self.fonts["body_bold"], cursor="hand2")
        logout.pack(anchor="w")
        logout.bind("<Button-1>", lambda e: self._handle_logout())
        tk.Label(footer, text="TQM Q09 — Reduce Bugs", bg=COLORS["sidebar_bg"], fg=COLORS["text_tertiary"],
                  font=self.fonts["small"]).pack(anchor="w", pady=(6, 0))

    def _build_topbar(self, parent):
        bar = tk.Frame(parent, bg=COLORS["background"], height=64)
        bar.pack(fill="x", padx=28)
        bar.pack_propagate(False)

        self.crumb = tk.Label(bar, text="", bg=COLORS["background"], fg=COLORS["text_tertiary"],
                               font=self.fonts["label"])
        self.crumb.pack(side="left")

        account = tk.Frame(bar, bg=COLORS["background"])
        account.pack(side="right")
        self.avatar = tk.Canvas(account, width=38, height=38, bg=COLORS["background"], highlightthickness=0)
        self.avatar.pack(side="right", padx=(10, 0))
        names = tk.Frame(account, bg=COLORS["background"])
        names.pack(side="right")
        self.account_name = tk.Label(names, text="", bg=COLORS["background"], fg=COLORS["text_primary"],
                                      font=self.fonts["body_bold"])
        self.account_name.pack(anchor="e")
        self.account_role = tk.Label(names, text="", bg=COLORS["background"], fg=COLORS["text_tertiary"],
                                      font=self.fonts["small"])
        self.account_role.pack(anchor="e")

        tk.Frame(account, bg=COLORS["border_strong"], width=1, height=28).pack(side="right", padx=16)
        clock = tk.Frame(account, bg=COLORS["background"])
        clock.pack(side="right")
        self.clock_time = tk.Label(clock, text="", bg=COLORS["background"], fg=COLORS["text_primary"],
                                    font=self.fonts["body_bold"])
        self.clock_time.pack(anchor="e")
        self.clock_date = tk.Label(clock, text="", bg=COLORS["background"], fg=COLORS["text_tertiary"],
                                    font=self.fonts["small"])
        self.clock_date.pack(anchor="e")

    def destroy(self):
        job = getattr(self, "_tick_job", None)
        if job:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        super().destroy()

    def _check_idle(self):
        if session.is_logged_in() and self._idle.expired():
            log_audit("Auth", "IdleLogout", session.get_user(), "Success",
                       f"'{session.get_user()}' was logged out after {IDLE_TIMEOUT_MINUTES} minutes of inactivity.")
            self._handle_logout()
            messagebox.showinfo("Logged out", f"You were logged out after {IDLE_TIMEOUT_MINUTES} minutes of "
                                              "inactivity. Please log in again.", parent=self)

    def _tick(self):
        self._check_idle()
        now = datetime.now()
        self.clock_time.configure(text=now.strftime("%I:%M:%S %p"))
        self.clock_date.configure(text=now.strftime("%a, %d %b %Y"))
        self._tick_job = self.after(1000, self._tick)

    def _update_account_info(self, user: dict):
        self.account_name.configure(text=user["username"].replace("_", " ").title())
        self.account_role.configure(text=user["role"])
        self.avatar.delete("all")
        self.avatar.create_oval(0, 0, 37, 37, fill=COLORS["accent"], outline="")
        self.avatar.create_text(19, 19, text=initials(user["username"]), fill="#FFFFFF",
                                font=self.fonts["body_bold"])

    # ------------------------------------------------------------ screens
    def _create_screens(self):
        self.screens["Dashboard"] = DashboardScreen(self.content, self.fonts, navigate=self.show_screen)
        self.screens["Calendar"] = CalendarScreen(self.content, self.fonts)
        self.screens["Students"] = StudentScreen(self.content, self.fonts)
        self.screens["Rooms"] = RoomScreen(self.content, self.fonts)
        self.screens["Allocation"] = AllocationScreen(self.content, self.fonts)
        self.screens["Complaints"] = ComplaintScreen(self.content, self.fonts)
        self.screens["Leaves"] = LeaveScreen(self.content, self.fonts)
        self.screens["Bugs"] = BugScreen(self.content, self.fonts)
        self.screens["Quality"] = QualityScreen(self.content, self.fonts)
        self.screens["Users"] = UserScreen(self.content, self.fonts)
        self.screens["MyRoom"] = MyRoomScreen(self.content, self.fonts)
        self.screens["MyComplaints"] = MyComplaintsScreen(self.content, self.fonts)
        self.screens["MyLeave"] = MyLeaveScreen(self.content, self.fonts)
        self.screens["MyDetails"] = MyDetailsScreen(self.content, self.fonts)
        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_screen(self, key: str):
        if key not in _allowed_screens(session.get_role()):
            return
        self._current = key
        self.screens[key].tkraise()
        self.screens[key].refresh()
        labels = {k: label for k, label, _ in _NAV_ITEMS}
        self.crumb.configure(text=f"Hostel MS  /  {labels[key]}")
        for nav_key, item in self._nav_items.items():
            item.set_active(nav_key == key)
