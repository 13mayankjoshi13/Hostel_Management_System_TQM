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
            ic = icon_circle(card.body, icon, fg, soft, size=34, bg=COLORS["surface"])
            ic.pack(side="left")
            text = tk.Frame(card.body, bg=COLORS["surface"])
            text.pack(side="left", padx=(10, 0))
            lbl_v = tk.Label(text, text=value, bg=COLORS["surface"], fg=COLORS["text_primary"],
                             font=self.fonts["stat_value"])
            lbl_v.pack(anchor="w")
            lbl_l = tk.Label(text, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                             font=self.fonts["small"])
            lbl_l.pack(anchor="w")

            def _stat_click(lbl=label, val=value, cname=self._name, ic=icon, col=fg, p=self):
                from app.theme import show_detail_dialog
                cat = str(cname).replace("_", " ").title()
                title = f"{lbl} — {cat}"
                subtitle = f"Overview and status for {cat}"
                fields = [("Category", cat), ("Metric", lbl), ("Current Count", str(val))]
                details = f"{lbl} in {cat} is currently {val}."

                cat_low = cat.lower()
                lbl_low = str(lbl).lower()

                try:
                    if "leave" in cat_low:
                        if "on leave" in lbl_low:
                            title = "Hostellers Currently on Leave"
                            subtitle = "Active leave permits requiring return check-in"
                            fields = [("Status", "On Leave"), ("Total Hostellers Away", str(val)), ("Policy", "Warden verification required on check-in")]
                            rows = [l for l in leave_service.get_all_leaves() if l.get("status") == "On Leave"]
                            if rows:
                                lines = [f"• {l.get('student_name', 'Student')} (Room {l.get('room_number', '-')}) — From {l.get('from_date')} to {l.get('to_date')}\n  Reason: {l.get('reason', 'N/A')}" for l in rows[:10]]
                                details = "Hostellers currently away on approved leave:\n\n" + "\n\n".join(lines)
                            else:
                                details = "All hostellers are currently present inside the hostel campus. No active leaves."
                        elif "returned" in lbl_low:
                            title = "Returned Hostellers"
                            subtitle = "Completed leaves verified by administration"
                            fields = [("Status", "Returned"), ("Completed Records", str(val))]
                            rows = [l for l in leave_service.get_all_leaves() if l.get("status") == "Returned"]
                            if rows:
                                lines = [f"• {l.get('student_name', 'Student')} (Room {l.get('room_number', '-')}) — Return verified (Leave: {l.get('from_date')} to {l.get('to_date')})" for l in rows[:10]]
                                details = "Recently returned hostellers:\n" + "\n".join(lines)
                            else:
                                details = "No returned leave records found."
                        else:
                            title = "Hostel Leave Records"
                            subtitle = "Cumulative leave requests and status overview"
                            details = f"A total of {val} leave applications are currently on record in the hostel tracking system."

                    elif "allocation" in cat_low:
                        if "active" in lbl_low:
                            title = "Active Room Allocations"
                            subtitle = "Hostellers currently assigned to rooms"
                            fields = [("Occupied Beds", str(val)), ("Status", "Active Resident Allocation")]
                            allocs = allocation_service.get_active_allocations()
                            if allocs:
                                lines = [f"• Room {a.get('room_number', '-')} ({a.get('hostel_type', 'Hostel')}): {a.get('student_name', 'Student')} (Allocated: {str(a.get('allocated_at', ''))[:10]})" for a in allocs[:10]]
                                details = f"Active room allocation records ({len(allocs)} total):\n" + "\n".join(lines)
                            else:
                                details = "No active room allocations currently in the database."
                        elif "beds free" in lbl_low:
                            title = "Available Free Beds"
                            subtitle = "Vacant capacity ready for student assignment"
                            fields = [("Free Beds", str(val)), ("Availability", "Open for Allocation")]
                            rooms = [r for r in home_service.floor_plan() if r["capacity"] > r["taken"]]
                            if rooms:
                                lines = [f"• Room {r['room_number']} ({r.get('hostel_type', 'Hostel')} · Floor {r.get('floor', 0)}): {r['capacity'] - r['taken']} free bed(s) out of {r['capacity']}" for r in rooms[:10]]
                                details = f"Rooms with free bed capacity ({len(rooms)} rooms):\n" + "\n".join(lines)
                            else:
                                details = "All hostel beds are currently occupied. Capacity is at 100%."
                        elif "without a room" in lbl_low:
                            title = "Students Awaiting Room Allocation"
                            subtitle = "Registered hostellers without active bed assignment"
                            fields = [("Awaiting Allocation", str(val)), ("Action Required", "Assign room in Room Allocation module")]
                            active_ids = {a["student_id"] for a in allocation_service.get_active_allocations()}
                            unhoused = [s for s in student_service.get_all_students() if s["student_id"] not in active_ids]
                            if unhoused:
                                lines = [f"• {s['name']} (Reg: {s['registration_number']}, Contact: {s.get('contact_number', 'N/A')})" for s in unhoused[:10]]
                                details = f"Registered students awaiting room assignment ({len(unhoused)}):\n" + "\n".join(lines)
                            else:
                                details = "Every registered student currently has an active room allocation."

                    elif "student" in cat_low:
                        if "without a room" in lbl_low:
                            title = "Unallocated Students"
                            subtitle = "Registered hostellers without room assignment"
                            fields = [("Unallocated", str(val)), ("Action", "Assign room in Allocation")]
                            active_ids = {a["student_id"] for a in allocation_service.get_active_allocations()}
                            unhoused = [s for s in student_service.get_all_students() if s["student_id"] not in active_ids]
                            if unhoused:
                                lines = [f"• {s['name']} (Reg: {s['registration_number']}) — Contact: {s.get('contact_number', '—')}" for s in unhoused[:10]]
                                details = "Students waiting for room allocation:\n" + "\n".join(lines)
                            else:
                                details = "All students currently have rooms assigned."
                        elif "with a room" in lbl_low:
                            title = "Accommodated Students"
                            subtitle = "Students actively allocated to hostel rooms"
                            fields = [("Accommodated", str(val)), ("Status", "Active Residents")]
                            details = f"Currently {val} hostellers have confirmed room allocations."
                        elif "gender" in lbl_low:
                            title = "Incomplete Student Profiles"
                            subtitle = "Hostellers missing gender specification"
                            fields = [("Unset Profiles", str(val)), ("Action", "Update profile in Students screen")]
                            no_gender = [s for s in student_service.get_all_students() if not s.get("gender")]
                            if no_gender:
                                lines = [f"• {s['name']} (Reg: {s['registration_number']})" for s in no_gender[:10]]
                                details = "Students with gender not set in their profile:\n" + "\n".join(lines)
                            else:
                                details = "All hostellers have gender specified."
                        else:
                            title = "Enrolled Hostellers"
                            subtitle = "Total students registered in hostel records"
                            details = f"Total enrolled hostellers: {val}. Review and manage individual records in the table below."

                    elif "complaint" in cat_low:
                        title = f"{lbl} Complaints"
                        subtitle = "Maintenance and hosteller issue resolution"
                        fields = [("Complaint Status", lbl), ("Count", str(val))]
                        if lbl_low in ("open", "assigned", "resolved"):
                            matched = [c for c in complaint_service.get_all_complaints() if str(c.get("status", "")).lower() == lbl_low]
                            if matched:
                                lines = [f"• #{c['complaint_id']} [{c.get('category', 'General')}] (Room {c.get('room_number', '-')}, {c.get('student_name', 'Student')}):\n  {str(c.get('description', ''))[:80]}" for c in matched[:8]]
                                details = f"{lbl} complaints ({len(matched)} total):\n\n" + "\n\n".join(lines)
                            else:
                                details = f"There are currently no {lbl.lower()} complaints."
                        else:
                            details = f"Total logged complaints in the system: {val} across all maintenance categories."

                    elif "event" in cat_low:
                        title = f"{lbl} Events"
                        subtitle = "Hostel and university calendar schedule"
                        fields = [("Event Type / Filter", lbl), ("Total Count", str(val))]
                        evts = event_service.get_upcoming(date.today().isoformat(), 15)
                        if lbl_low != "upcoming":
                            evts = [e for e in evts if str(e.get("kind", "")).lower() == lbl_low.replace("s", "")]
                        if evts:
                            lines = [f"• {e['event_date']} — {e['title']} ({e.get('kind', 'Event')})" for e in evts[:8]]
                            details = f"Scheduled items ({len(evts)}):\n" + "\n".join(lines)
                        else:
                            details = f"No upcoming {lbl.lower()} scheduled on the calendar."

                    elif "fine" in cat_low:
                        title = f"Hostel Fines — {lbl}"
                        subtitle = "Disciplinary charges and fee collections"
                        fields = [("Fine Status", lbl), ("Amount / Count", str(val))]
                        fines = fine_service.get_all_fines()
                        if "unpaid" in lbl_low or "due" in lbl_low:
                            unpaid = [f for f in fines if f.get("status") == "Unpaid"]
                            if unpaid:
                                lines = [f"• Fine #{f['fine_id']} — {f.get('student_name', 'Student')} (Room {f.get('room_number', '-')}): ₹{f['amount_paise'] / 100:.2f} — {f.get('reason', 'Fine')}" for f in unpaid[:8]]
                                details = f"Unpaid fines awaiting settlement ({len(unpaid)}):\n" + "\n".join(lines)
                            else:
                                details = "No outstanding unpaid fines. All accounts settled."
                        else:
                            details = f"Hostel fines summary for '{lbl}': {val}."

                    elif "contact" in cat_low:
                        if "warden" in lbl_low:
                            title = "Hostel Wardens Directory"
                            subtitle = "Administrative oversight contacts"
                            wardens = warden_service.list_wardens()
                            if wardens:
                                lines = [f"• {w['name']} ({w['hostel_name']}) — Contact: {w['contact_number']}, Office hours: {w.get('office_hours', '—')}" for w in wardens]
                                details = "Hostel Wardens:\n" + "\n".join(lines)
                        elif "emergency" in lbl_low:
                            title = "Emergency & University Helplines"
                            subtitle = "Essential contacts, medical and university support"
                            conts = emergency_service.list_contacts()
                            if conts:
                                lines = [f"• {c['name']} ({c['category']}): {c['number']}" for c in conts[:10]]
                                details = "Helpline Directory:\n" + "\n".join(lines)

                except Exception:
                    pass

                show_detail_dialog(
                    parent=p,
                    title=title,
                    subtitle=subtitle,
                    icon=ic,
                    color=col,
                    fields=fields,
                    full_text=details
                )

            from app.theme import make_clickable
            for widget in (card, card.body, text, lbl_v, lbl_l, ic):
                make_clickable(widget, _stat_click)



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
