"""Shift log: each specialist role records its own issues and follow-ups; wardens and admins can read all."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.validation import ValidationError

KINDS = {
    "Mess Staff": ("Stock shortage", "Food wastage", "Hygiene check", "Meal delayed", "Equipment fault"),
    "Maintenance Staff": ("Parts needed", "Safety hazard", "Scheduled repair", "Vendor call", "Equipment fault"),
    "Security Staff": ("Incident", "Lost and found", "Patrol round", "Suspicious activity", "Gate fault"),
    "Housekeeping Staff": ("Supplies low", "Pest report", "Deep clean", "Garbage pickup", "Equipment fault"),
}


def kinds_for_role() -> tuple:
    return KINDS.get(session.get_role(), ())


def add_entry(kind: str, details: str) -> None:
    session.require_roles(tuple(KINDS), "write shift log entries")
    if kind not in kinds_for_role():
        raise ValidationError("Choose a type from the list.")
    details = " ".join((details or "").split())
    if len(details) < 5:
        raise ValidationError("Describe it in at least 5 characters.")
    if len(details) > 300:
        raise ValidationError("The description must be 300 characters or fewer.")
    conn = get_connection()
    try:
        conn.execute("INSERT INTO staff_log (role, kind, details, created_by) VALUES (?, ?, ?, ?)",
                     (session.get_role(), kind, details, session.get_user()))
        conn.commit()
        log_audit("ShiftLog", "Add", kind, "Success", "Entry added.")
    except sqlite3.Error as exc:
        log_error("ShiftLog", "DatabaseError", "High", "add_entry", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the entry due to a database error.")
    finally:
        conn.close()


def mark_done(log_id) -> None:
    session.require_roles(tuple(KINDS), "close shift log entries")
    conn = get_connection()
    try:
        conn.execute("UPDATE staff_log SET status = 'Done', done_at = datetime('now') WHERE log_id = ? AND role = ?",
                     (int(log_id), session.get_role()))
        conn.commit()
        log_audit("ShiftLog", "Done", str(log_id), "Success", "Entry closed.")
    except sqlite3.Error as exc:
        log_error("ShiftLog", "DatabaseError", "High", "mark_done", status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the entry due to a database error.")
    finally:
        conn.close()


def list_entries(open_only: bool = False, limit: int = 200) -> list:
    """Own role's entries for specialists; every role's for wardens and admins."""
    session.require_roles(session.WARDEN_ROLES + tuple(KINDS), "view the shift log")
    sql = "SELECT log_id, role, kind, details, status, created_by, created_at FROM staff_log WHERE 1=1"
    args = []
    if session.get_role() in KINDS:
        sql += " AND role = ?"
        args.append(session.get_role())
    if open_only:
        sql += " AND status = 'Open'"
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(sql + " ORDER BY log_id DESC LIMIT ?", (*args, int(limit)))]
    finally:
        conn.close()


def open_count() -> int:
    return len(list_entries(open_only=True))
