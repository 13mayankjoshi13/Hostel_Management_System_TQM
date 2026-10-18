"""
Leave tracking: which student is on leave, from which room.

Status flow: On Leave -> Returned (forward only). A leave can only be
recorded for a student who currently has an Active room allocation, and
a student cannot have two open leaves at once.
"""
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils.validation import validate_leave_dates, validate_leave_reason, validate_record_id, ValidationError
from app.utils.logging_service import log_error, log_audit


def record_leave(student_id: int, from_date: str, to_date: str, reason: str) -> int:
    student_id = validate_record_id(student_id, "Please select a student.")
    start, end = validate_leave_dates(from_date, to_date)
    clean_reason = validate_leave_reason(reason)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT room_id FROM allocations WHERE student_id = ? AND status = 'Active'",
                    (student_id,))
        allocation = cur.fetchone()
        if allocation is None:
            raise ValidationError("This student has no active room allocation, so no leave can be recorded.")
        cur.execute("SELECT leave_id FROM leaves WHERE student_id = ? AND status = 'On Leave'",
                    (student_id,))
        if cur.fetchone() is not None:
            raise ValidationError("This student already has an open leave. Mark it as returned first.")

        cur.execute(
            "INSERT INTO leaves (student_id, room_id, from_date, to_date, reason) VALUES (?, ?, ?, ?, ?)",
            (student_id, allocation["room_id"], start, end, clean_reason))
        conn.commit()
        leave_id = cur.lastrowid
        log_audit("Leave", "Create", str(leave_id), "Success",
                   f"Leave recorded for student {student_id} ({start} to {end}).")
        return leave_id
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Leave", "DatabaseError", "High", "record_leave",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the leave due to a database error.")
    finally:
        conn.close()


def mark_returned(leave_id: int) -> None:
    leave_id = validate_record_id(leave_id, "Please select a valid leave.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT status FROM leaves WHERE leave_id = ?", (leave_id,))
        leave = cur.fetchone()
        if leave is None:
            raise ValidationError(f"No leave found with ID {leave_id}.")
        if leave["status"] != "On Leave":
            raise ValidationError("This student is already marked as returned.")
        cur.execute("UPDATE leaves SET status = 'Returned', returned_at = ? WHERE leave_id = ?",
                    (datetime.now().isoformat(timespec="seconds"), leave_id))
        conn.commit()
        log_audit("Leave", "Return", str(leave_id), "Success", "Student marked as returned.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Leave", "DatabaseError", "High", "mark_returned",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the leave due to a database error.")
    finally:
        conn.close()


def get_all_leaves() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT l.leave_id, s.name AS student_name, r.room_number,
                   l.from_date, l.to_date, l.reason, l.status
            FROM leaves l
            JOIN students s ON s.student_id = l.student_id
            JOIN rooms r ON r.room_id = l.room_id
            ORDER BY l.leave_id DESC
        """)
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Leave", "DatabaseError", "Medium", "get_all_leaves",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()
