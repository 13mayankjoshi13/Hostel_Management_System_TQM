"""Data for the home pages: one student's own summary, and the hostel floor plan."""
from datetime import date

from app.database.db import get_connection
from app.services import (attendance_service, emergency_service, event_service, fine_service,
                          notice_service, warden_service)
from app.utils import session
from app.utils.validation import ValidationError


def student_home() -> dict:
    """Everything a student's front page shows, for the logged-in student only."""
    if session.get_role() != "Student" or session.get_student_id() is None:
        raise ValidationError("This page is only available to student accounts.")
    sid = session.get_student_id()
    conn = get_connection()
    try:
        student = conn.execute("SELECT name, gender FROM students WHERE student_id = ?", (sid,)).fetchone()
        room = conn.execute(
            "SELECT r.room_number, r.room_type, r.floor, r.hostel_type FROM allocations a "
            "JOIN rooms r ON r.room_id = a.room_id WHERE a.student_id = ? AND a.status = 'Active'",
            (sid,)).fetchone()
    finally:
        conn.close()
    if student is None:
        raise ValidationError("Your student record was not found. Contact the hostel office.")
    fines = [f for f in fine_service.get_fines_for_student(sid) if f["status"] == "Unpaid"]
    today = date.today().isoformat()
    return {
        "name": student["name"],
        "gender": student["gender"],
        "room": dict(room) if room else None,
        "attendance": attendance_service.student_summary(sid, 30),
        "notices": notice_service.notices_for_student(sid, limit=3),
        "fines_due": fines,
        "fines_due_paise": sum(f["amount_paise"] for f in fines),
        "warden": warden_service.warden_for_student(sid),
        "emergency": emergency_service.list_contacts(),
        "events": event_service.get_upcoming(today, 4),
    }


def staff_home() -> dict:
    """Attendance totals for today and the latest notices, for staff dashboards."""
    session.require_roles(session.STAFF_ROLES, "view the staff summary")
    return {
        "attendance": attendance_service.attendance_counts(),
        "notices": notice_service.list_notices(limit=5),
    }


def floor_plan() -> list:
    """Rooms grouped by hostel and floor with bed counts. Names are shown to staff only."""
    show_names = session.get_role() in session.STAFF_ROLES
    conn = get_connection()
    try:
        rooms = [dict(r) for r in conn.execute(
            "SELECT r.room_id, r.room_number, r.room_type, r.capacity, r.floor, r.hostel_type, "
            "COUNT(a.allocation_id) AS taken FROM rooms r LEFT JOIN allocations a "
            "ON a.room_id = r.room_id AND a.status = 'Active' GROUP BY r.room_id "
            "ORDER BY r.hostel_type, r.floor DESC, r.room_number")]
        for room in rooms:
            room["occupants"] = []
            if show_names:
                room["occupants"] = [row["name"] for row in conn.execute(
                    "SELECT s.name FROM allocations a JOIN students s ON s.student_id = a.student_id "
                    "WHERE a.room_id = ? AND a.status = 'Active' ORDER BY s.name", (room["room_id"],))]
        return rooms
    finally:
        conn.close()


def my_room_number():
    if session.get_role() != "Student" or session.get_student_id() is None:
        return None
    conn = get_connection()
    try:
        row = conn.execute("SELECT r.room_number FROM allocations a JOIN rooms r ON r.room_id = a.room_id "
                           "WHERE a.student_id = ? AND a.status = 'Active'", (session.get_student_id(),)).fetchone()
        return row["room_number"] if row else None
    finally:
        conn.close()
