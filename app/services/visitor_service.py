"""Visitor and gate log: staff check visitors in and out; visits outside visiting hours are flagged."""
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.timefmt import localise_rows, utc_now
from app.utils.validation import ValidationError, validate_contact_number, validate_record_id

RELATIONS = ("Parent", "Sibling", "Relative", "Friend", "Guardian", "Other")
VISIT_START_HOUR = 9
VISIT_END_HOUR = 19


def _clean(value: str, label: str, limit: int) -> str:
    value = " ".join((value or "").split())
    if len(value) < 2:
        raise ValidationError(f"{label} must be at least 2 characters.")
    if len(value) > limit:
        raise ValidationError(f"{label} must be {limit} characters or fewer.")
    return value


def log_visitor(student_id: int, visitor_name: str, relation: str, phone: str, purpose: str) -> int:
    session.require_roles(session.VISITOR_ROLES, "log visitors")
    student_id = validate_record_id(student_id, "Select the student being visited.")
    name = _clean(visitor_name, "Visitor name", 60)
    purpose = _clean(purpose, "Purpose", 100)
    if relation not in RELATIONS:
        raise ValidationError("Choose the visitor's relation to the student.")
    phone = validate_contact_number(phone) if (phone or "").strip() else ""
    conn = get_connection()
    try:
        if conn.execute("SELECT 1 FROM allocations WHERE student_id = ? AND status = 'Active'",
                        (student_id,)).fetchone() is None:
            raise ValidationError("This student has no active room, so they cannot receive visitors.")
        cur = conn.execute(
            "INSERT INTO visitors (student_id, visitor_name, relation, phone, purpose, in_time, logged_by) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (student_id, name, relation, phone, purpose, utc_now(), session.get_user()))
        conn.commit()
        log_audit("Visitor", "CheckIn", str(cur.lastrowid), "Success", f"{name} visiting student {student_id}.")
        return cur.lastrowid
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Visitor", "DatabaseError", "High", "log_visitor", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the visitor due to a database error.")
    finally:
        conn.close()


def check_out(visitor_id: int) -> None:
    session.require_roles(session.VISITOR_ROLES, "check visitors out")
    visitor_id = validate_record_id(visitor_id, "Select a visitor first.")
    conn = get_connection()
    try:
        row = conn.execute("SELECT out_time FROM visitors WHERE visitor_id = ?", (visitor_id,)).fetchone()
        if row is None:
            raise ValidationError(f"No visitor found with ID {visitor_id}.")
        if row["out_time"]:
            raise ValidationError("This visitor has already been checked out.")
        conn.execute("UPDATE visitors SET out_time = ? WHERE visitor_id = ?", (utc_now(), visitor_id))
        conn.commit()
        log_audit("Visitor", "CheckOut", str(visitor_id), "Success", "Visitor checked out.")
    finally:
        conn.close()


def _flag(row: dict) -> str:
    inside_hour = datetime.fromisoformat(row["in_time"]).hour
    if not VISIT_START_HOUR <= inside_hour < VISIT_END_HOUR:
        return "After hours"
    if row["out_time"] and datetime.fromisoformat(row["out_time"]).hour >= VISIT_END_HOUR:
        return "Overstayed"
    return ""


def list_visitors(inside_only: bool = False, limit: int = 200) -> list:
    session.require_roles(session.VISITOR_ROLES, "view the visitor log")
    conn = get_connection()
    try:
        sql = ("SELECT v.visitor_id, s.name AS student_name, r.room_number, v.visitor_name, v.relation, v.phone, "
               "v.purpose, v.in_time, v.out_time FROM visitors v JOIN students s ON s.student_id = v.student_id "
               "LEFT JOIN allocations al ON al.student_id = v.student_id AND al.status = 'Active' "
               "LEFT JOIN rooms r ON r.room_id = al.room_id ")
        if inside_only:
            sql += "WHERE v.out_time IS NULL "
        rows = localise_rows([dict(r) for r in conn.execute(sql + "ORDER BY v.visitor_id DESC LIMIT ?",
                                                             (int(limit),)).fetchall()], "in_time", "out_time")
        for row in rows:
            row["flag"] = _flag(row) if row["in_time"] else ""
            row["room_number"] = row["room_number"] or "—"
        return rows
    finally:
        conn.close()


def inside_count() -> int:
    session.require_roles(session.VISITOR_ROLES, "view the visitor log")
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM visitors WHERE out_time IS NULL").fetchone()[0]
    finally:
        conn.close()


def visit_targets() -> list:
    """Students with an active room, for the check-in drop-down."""
    session.require_roles(session.VISITOR_ROLES, "view students with rooms")
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT s.student_id, s.name AS student_name, r.room_number FROM allocations al "
            "JOIN students s ON s.student_id = al.student_id JOIN rooms r ON r.room_id = al.room_id "
            "WHERE al.status = 'Active' ORDER BY s.name")]
    finally:
        conn.close()
