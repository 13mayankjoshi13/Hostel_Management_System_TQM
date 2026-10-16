"""
Student self-service. Every function acts on the logged-in student's own
records only: the student ID always comes from the session, never from
the caller, so one student can never read or change another's data.
"""
import sqlite3

from app.database.db import get_connection
from app.services import complaint_service, leave_service, student_service
from app.utils import session
from app.utils.logging_service import log_error
from app.utils.validation import ValidationError


def _current_student_id() -> int:
    if session.get_role() != "Student" or session.get_student_id() is None:
        raise ValidationError("This action is only available to student accounts.")
    return session.get_student_id()


def _query(sql: str, params: tuple, action: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Portal", "DatabaseError", "Medium", action,
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def my_room():
    """The student's active room, or None."""
    sid = _current_student_id()
    rows = _query("""
        SELECT r.room_number, r.room_type, r.capacity, a.allocated_at
        FROM allocations a JOIN rooms r ON r.room_id = a.room_id
        WHERE a.student_id = ? AND a.status = 'Active'
    """, (sid,), "my_room")
    return rows[0] if rows else None


def my_complaints() -> list:
    sid = _current_student_id()
    return _query("""
        SELECT complaint_id, category, description, status, assigned_to, created_at, resolution_notes
        FROM complaints WHERE student_id = ? ORDER BY complaint_id DESC
    """, (sid,), "my_complaints")


def file_complaint(category: str, description: str) -> int:
    return complaint_service.create_complaint(_current_student_id(), category, description)


def my_leaves() -> list:
    sid = _current_student_id()
    return _query("""
        SELECT l.leave_id, r.room_number, l.from_date, l.to_date, l.reason, l.status
        FROM leaves l JOIN rooms r ON r.room_id = l.room_id
        WHERE l.student_id = ? ORDER BY l.leave_id DESC
    """, (sid,), "my_leaves")


def apply_leave(from_date: str, to_date: str, reason: str) -> int:
    return leave_service.record_leave(_current_student_id(), from_date, to_date, reason)


def return_from_leave(leave_id: int) -> None:
    sid = _current_student_id()
    owned = _query("SELECT leave_id FROM leaves WHERE leave_id = ? AND student_id = ?",
                   (leave_id, sid), "return_from_leave")
    if not owned:
        raise ValidationError("That leave record was not found.")
    leave_service.mark_returned(leave_id)


def my_details() -> dict:
    """The student's own record."""
    sid = _current_student_id()
    rows = _query("SELECT student_id, name, registration_number, contact_number FROM students "
                  "WHERE student_id = ?", (sid,), "my_details")
    return rows[0] if rows else {}


def update_my_details(name: str, contact_number: str) -> None:
    """Students may change their name and contact; the registration number stays as the hostel recorded it."""
    sid = _current_student_id()
    current = my_details()
    student_service._update(sid, name, current["registration_number"], contact_number)
