"""Notices: staff post to everyone, a hostel, or one student; students read only theirs."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.timefmt import localise_rows
from app.utils.validation import (
    NOTICE_AUDIENCES, ValidationError, validate_notice_body, validate_notice_title, validate_record_id,
)


def send_notice(title: str, body: str, audience: str, student_id=None) -> int:
    session.require_roles(session.STAFF_ROLES, "send notices")
    title = validate_notice_title(title)
    body = validate_notice_body(body)
    if audience not in NOTICE_AUDIENCES:
        raise ValidationError("Choose who the notice is for.")
    if audience == "Student":
        student_id = validate_record_id(student_id, "Select the student who should get this notice.")
    else:
        student_id = None

    conn = get_connection()
    try:
        cur = conn.cursor()
        if student_id is not None:
            cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
            if cur.fetchone() is None:
                raise ValidationError(f"No student found with ID {student_id}.")
        cur.execute(
            "INSERT INTO notices (title, body, audience, student_id, created_by) VALUES (?, ?, ?, ?, ?)",
            (title, body, audience, student_id, session.get_user()),
        )
        conn.commit()
        notice_id = cur.lastrowid
        log_audit("Notice", "Create", str(notice_id), "Success", f"Notice sent to {audience}.")
        return notice_id
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Notice", "DatabaseError", "High", "send_notice", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the notice due to a database error.")
    finally:
        conn.close()


def list_notices(limit: int = 200) -> list:
    session.require_roles(session.STAFF_ROLES, "view all notices")
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT n.*, s.name AS student_name FROM notices n LEFT JOIN students s "
            "ON s.student_id = n.student_id ORDER BY n.notice_id DESC LIMIT ?", (int(limit),)).fetchall()
        return localise_rows([dict(r) for r in rows], "created_at")
    finally:
        conn.close()


def notices_for_student(student_id=None, limit: int = 50) -> list:
    """Notices a student may see: all, their hostel's, or addressed to them."""
    if student_id is None:
        student_id = session.get_student_id()
    session.require_own_or_staff(student_id, "view these notices")
    conn = get_connection()
    try:
        student = conn.execute("SELECT gender FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if student is None:
            return []
        hostel = {"Male": "Boys", "Female": "Girls"}.get(student["gender"], "")
        rows = conn.execute(
            "SELECT notice_id, title, body, audience, created_by, created_at FROM notices "
            "WHERE audience = 'All' OR audience = ? OR (audience = 'Student' AND student_id = ?) "
            "ORDER BY notice_id DESC LIMIT ?", (hostel, student_id, int(limit))).fetchall()
        return localise_rows([dict(r) for r in rows], "created_at")
    finally:
        conn.close()


def delete_notice(notice_id: int) -> None:
    session.require_roles(session.ADMIN_ROLES, "delete notices")
    notice_id = validate_record_id(notice_id, "Select a notice first.")
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM notices WHERE notice_id = ?", (notice_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValidationError("That notice no longer exists.")
        log_audit("Notice", "Delete", str(notice_id), "Success", "Notice deleted.")
    finally:
        conn.close()
