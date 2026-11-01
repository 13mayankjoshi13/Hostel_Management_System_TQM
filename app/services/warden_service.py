"""Wardens: a girls' hostel student sees the female warden, a boys' hostel student the male warden."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.validation import (
    ValidationError, validate_assigned_to, validate_contact_number, validate_gender,
    validate_hostel_name, validate_record_id,
)


def add_warden(name: str, gender: str, contact_number: str, hostel_name: str, office_hours: str = "") -> int:
    session.require_roles(session.ADMIN_ROLES, "add wardens")
    clean_name = validate_assigned_to(name)
    if clean_name is None:
        raise ValidationError("Warden name cannot be empty.")
    clean_gender = validate_gender(gender)
    clean_contact = validate_contact_number(contact_number)
    clean_hostel = validate_hostel_name(hostel_name)
    hours = " ".join((office_hours or "").split())
    if len(hours) > 60:
        raise ValidationError("Office hours must be 60 characters or fewer.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO wardens (name, gender, contact_number, hostel_name, office_hours) VALUES (?, ?, ?, ?, ?)",
            (clean_name, clean_gender, clean_contact, clean_hostel, hours or None))
        conn.commit()
        log_audit("Warden", "Create", str(cur.lastrowid), "Success", f"Added warden '{clean_name}'.")
        return cur.lastrowid
    except sqlite3.Error as exc:
        log_error("Warden", "DatabaseError", "High", "add_warden", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the warden due to a database error.")
    finally:
        conn.close()


def list_wardens() -> list:
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM wardens WHERE status = 'Active' ORDER BY hostel_name, name").fetchall()]
    finally:
        conn.close()


def delete_warden(warden_id: int) -> None:
    session.require_roles(session.ADMIN_ROLES, "remove wardens")
    warden_id = validate_record_id(warden_id, "Select a warden first.")
    conn = get_connection()
    try:
        cur = conn.execute("UPDATE wardens SET status = 'Removed' WHERE warden_id = ? AND status = 'Active'",
                           (warden_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValidationError("That warden no longer exists.")
        log_audit("Warden", "Delete", str(warden_id), "Success", "Warden removed.")
    finally:
        conn.close()


def warden_for_student(student_id=None):
    """The warden of the student's own gender, or None when gender or warden is not set."""
    if student_id is None:
        student_id = session.get_student_id()
    session.require_own_or_staff(student_id, "view warden details")
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT w.* FROM wardens w JOIN students s ON s.gender = w.gender "
            "WHERE s.student_id = ? AND w.status = 'Active' ORDER BY w.warden_id LIMIT 1",
            (student_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
