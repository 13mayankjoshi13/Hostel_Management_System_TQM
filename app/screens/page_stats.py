"""Summary strip shown under each list screen's title, built from the same services the screen uses."""
import tkinter as tk
from datetime import date

from app.services import (allocation_service, attendance_service, auth_service, bug_service, complaint_service,
                          emergency_service, event_service, fine_service, home_service, leave_service,
                          notice_service, student_portal_service, student_service, warden_service, worker_service)
from app.theme import COLORS, Card, icon_circle
from app.utils import session
from app.utils.logging_service import log_error
from app.utils.validation import ValidationError


def _c(name):
    return COLORS[name], COLORS[name + "_soft"]


def _item(label, value, icon, colour):
    fg, soft = _c(colour) if colour != "accent" else (COLORS["accent"], COLORS["accent_soft"])
    return (label, str(value), icon, fg, soft)


def _count(rows, key, value):
    return sum(1 for r in rows if r.get(key) == value)


def _students():
    students, active = student_service.get_all_students(), allocation_service.get_active_allocations()
    housed = {a["student_id"] for a in active}
    return [_item("Students", len(students), "users", "accent"),
            _item("With a room", sum(1 for s in students if s["student_id"] in housed), "key", "teal"),
            _item("Without a room", sum(1 for s in students if s["student_id"] not in housed), "door", "orange"),
            _item("Gender not set", sum(1 for s in students if not s.get("gender")), "user", "pink")]


def _rooms():
    rooms = home_service.floor_plan()
    beds = sum(r["capacity"] for r in rooms)
    taken = sum(r["taken"] for r in rooms)
    return [_item("Rooms", len(rooms), "door", "accent"), _item("Beds", beds, "bed", "teal"),
            _item("Beds occupied", f"{round(taken / beds * 100) if beds else 0}%", "key", "info"),
            _item("Vacant rooms", sum(1 for r in rooms if r["taken"] == 0), "home", "success")]


def _allocation():
    rooms, active = home_service.floor_plan(), allocation_service.get_active_allocations()
    housed = {a["student_id"] for a in active}
    unhoused = sum(1 for s in student_service.get_all_students() if s["student_id"] not in housed)
    return [_item("Active allocations", len(active), "key", "accent"),
            _item("Beds free", sum(r["capacity"] - r["taken"] for r in rooms), "bed", "teal"),
            _item("Students without a room", unhoused, "users", "orange")]


def _complaints():
    rows = complaint_service.get_all_complaints()
    return [_item("Open", _count(rows, "status", "Open"), "chat", "orange"),
            _item("Assigned", _count(rows, "status", "Assigned"), "users", "info"),
            _item("Resolved", _count(rows, "status", "Resolved"), "clipboard", "success"),
            _item("Total", len(rows), "grid", "accent")]


def _leaves():
    rows = leave_service.get_all_leaves()
    return [_item("On leave now", _count(rows, "status", "On Leave"), "plane", "orange"),
            _item("Returned", _count(rows, "status", "Returned"), "key", "success"),
            _item("Total records", len(rows), "grid", "accent")]


def _fines():
    rows = fine_service.get_all_fines()
    due = sum(r["amount_paise"] for r in rows if r["status"] == "Unpaid")
    return [_item("Due", fine_service.format_rupees(due), "clipboard", "orange"),
            _item("Unpaid fines", _count(rows, "status", "Unpaid"), "chat", "pink"),
            _item("Paid", _count(rows, "status", "Paid"), "key", "success"),
            _item("Waived", _count(rows, "status", "Waived"), "grid", "info")]


def _workers():
    rows = worker_service.get_workers()
    active = [r for r in rows if r["status"] == "Active"]
    return [_item("Active workers", len(active), "users", "accent"),
            _item("Present today", _count(active, "today", "Present"), "key", "success"),
            _item("Open jobs", sum(r["open_jobs"] for r in rows), "chat", "orange"),
            _item("Jobs done", sum(r["done_jobs"] for r in rows), "clipboard", "teal")]


def _bugs():
    rows = bug_service.get_all_bugs()
    return [_item("Open", _count(rows, "status", "Open"), "bug", "pink"),
            _item("In progress", _count(rows, "status", "In Progress"), "grid", "info"),
            _item("Fixed", _count(rows, "status", "Fixed"), "key", "success"),
            _item("Closed", _count(rows, "status", "Closed"), "clipboard", "teal")]


def _users():
    rows = auth_service.list_users()
    return [_item("Accounts", len(rows), "users", "accent"),
            _item("Waiting for approval", _count(rows, "status", "Pending"), "chat", "orange"),
            _item("Students", _count(rows, "role", "Student"), "user", "teal"),
            _item("Admins", sum(1 for r in rows if r["role"] in session.ADMIN_ROLES), "key", "info")]


def _notices():
    rows = notice_service.list_notices()
    today = date.today().isoformat()
    return [_item("Notices sent", len(rows), "chat", "accent"),
            _item("Sent today", sum(1 for r in rows if str(r["created_at"]).startswith(today)), "calendar", "info"),
            _item("To one student", _count(rows, "audience", "Student"), "user", "teal")]


def _attendance():
    c = attendance_service.attendance_counts()
    return [_item("Present today", c["Present"], "users", "success"), _item("Absent today", c["Absent"], "chat", "pink"),
            _item("On leave", c["Leave"], "plane", "info"), _item("Not marked", c["Unmarked"], "clipboard", "orange")]


def _events():
    rows = event_service.get_upcoming(date.today().isoformat(), 500)
    return [_item("Upcoming", len(rows), "calendar", "accent"),
            _item("Hostel events", _count(rows, "kind", "Hostel Event"), "home", "teal"),
            _item("Holidays", _count(rows, "kind", "Holiday"), "key", "pink"),
            _item("Exams", _count(rows, "kind", "Exam"), "clipboard", "orange")]


def _contacts():
    wardens = [warden_service.warden_for_student()] if session.get_role() == "Student" else warden_service.list_wardens()
    return [_item("Wardens", len([w for w in wardens if w]), "users", "accent"),
            _item("Emergency numbers", len(emergency_service.list_contacts()), "chat", "pink")]


def _my_complaints():
    rows = student_portal_service.my_complaints()
    return [_item("Open", _count(rows, "status", "Open") + _count(rows, "status", "Assigned"), "chat", "orange"),
            _item("Resolved", _count(rows, "status", "Resolved"), "clipboard", "success"),
            _item("Total", len(rows), "grid", "accent")]


def _my_leave():
    rows = student_portal_service.my_leaves()
    return [_item("On leave now", _count(rows, "status", "On Leave"), "plane", "orange"),
            _item("Total", len(rows), "grid", "accent")]


def _my_fines():
    rows = student_portal_service.my_fines()
    due = sum(r["amount_paise"] for r in rows if r["status"] == "Unpaid")
    return [_item("Due", fine_service.format_rupees(due), "clipboard", "orange"),
            _item("Paid", _count(rows, "status", "Paid"), "key", "success"),
            _item("Total", len(rows), "grid", "accent")]


def _my_notices():
    return [_item("Notices for you", len(notice_service.notices_for_student()), "chat", "accent")]


PROVIDERS = {"Students": _students, "Rooms": _rooms, "Allocation": _allocation, "Complaints": _complaints,
             "Leaves": _leaves, "Fines": _fines, "Workers": _workers, "Bugs": _bugs, "Users": _users,
             "Notices": _notices, "Attendance": _attendance, "Events": _events, "Contacts": _contacts,
             "MyComplaints": _my_complaints, "MyLeave": _my_leave, "MyFines": _my_fines, "MyNotices": _my_notices}


class StatStrip(tk.Frame):
    def __init__(self, parent, fonts, provider, name):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts, self._provider, self._name = fonts, provider, name

    def update_stats(self):
        try:
            items = self._provider()
        except ValidationError:
            items = []
        except Exception as exc:
            log_error("Screen", type(exc).__name__, "Low", f"stats_{self._name}", status="Open", message_reference=str(exc))
            items = []
        for child in self.winfo_children():
            child.destroy()
        for i, (label, value, icon, fg, soft) in enumerate(items):
            self.columnconfigure(i, weight=1, uniform="stat")
            card = Card(self, pad=10, radius=14, fit=True)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 5, 0 if i == len(items) - 1 else 5))
            icon_circle(card.body, icon, fg, soft, size=34, bg=COLORS["surface"]).pack(side="left")
            text = tk.Frame(card.body, bg=COLORS["surface"])
            text.pack(side="left", padx=(10, 0))
            tk.Label(text, text=value, bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["stat_value"]).pack(anchor="w")
            tk.Label(text, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["small"]).pack(anchor="w")


def attach(screen, key, fonts):
    """Put a summary strip under the screen's title and keep it current whenever the screen refreshes."""
    provider = PROVIDERS.get(key)
    if provider is None:
        return None
    header = screen.pack_slaves()[0] if screen.pack_slaves() else None
    strip = StatStrip(screen, fonts, provider, key)
    strip.pack(fill="x", padx=28, pady=(0, 12), **({"after": header} if header is not None else {}))
    original = screen.refresh

    def refresh():
        original()
        strip.update_stats()

    screen.refresh = refresh
    screen.stat_strip = strip
    return strip
