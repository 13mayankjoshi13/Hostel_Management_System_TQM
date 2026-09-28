"""
Complaint Management service.

Status flow (Strict Validation — "Invalid complaint status -> reject",
FULL PROJECT CONTEXT section 16.2):

    Open  ---assign--->  Assigned  ---resolve--->  Resolved
      |                                                ^
      +------------------ resolve ---------------------+

A complaint can be resolved directly from "Open" (a warden may fix a
simple issue without a formal assignment step) or from "Assigned". It
can never move backward, and an already-Resolved complaint can never be
assigned or resolved again — every transition is checked before any
write, same prevention-at-source pattern as the other services.
"""
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils.validation import (
    validate_complaint_category,
    validate_complaint_description,
    validate_assigned_to,
    validate_resolution_notes,
    ValidationError,
)
from app.utils.logging_service import log_error, log_audit

_ASSIGNABLE_STATUSES = {"Open"}
_RESOLVABLE_STATUSES = {"Open", "Assigned"}


def _get_complaint_or_raise(cur, complaint_id: int) -> sqlite3.Row:
    cur.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    complaint = cur.fetchone()
    if complaint is None:
        raise ValidationError(f"No complaint found with ID {complaint_id}.")
    return complaint


def create_complaint(student_id: int, category: str, description: str) -> int:
    """Validate and insert a new complaint with status 'Open'."""
    try:
        student_id = int(student_id)
    except (TypeError, ValueError):
        raise ValidationError("Please select a student.")

    clean_category = validate_complaint_category(category)
    clean_description = validate_complaint_description(description)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if cur.fetchone() is None:
            raise ValidationError(f"No student found with ID {student_id}.")

        cur.execute(
            "INSERT INTO complaints (student_id, category, description, status) "
            "VALUES (?, ?, ?, 'Open')",
            (student_id, clean_category, clean_description),
        )
        conn.commit()
        complaint_id = cur.lastrowid
        log_audit("Complaint", "Create", str(complaint_id), "Success",
                   f"Logged '{clean_category}' complaint for student {student_id}.")
        return complaint_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Complaint", "DatabaseError", "High", "create_complaint",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the complaint due to a database error.")
    finally:
        conn.close()


def assign_complaint(complaint_id: int, assigned_to: str) -> None:
    """Move a complaint from 'Open' to 'Assigned'. Rejects any other status."""
    clean_assigned_to = validate_assigned_to(assigned_to)

    conn = get_connection()
    try:
        cur = conn.cursor()
        complaint = _get_complaint_or_raise(cur, complaint_id)

        if complaint["status"] not in _ASSIGNABLE_STATUSES:
            raise ValidationError(
                f"Cannot assign a complaint with status '{complaint['status']}'. "
                f"Only 'Open' complaints can be assigned."
            )

        cur.execute(
            "UPDATE complaints SET status = 'Assigned', assigned_to = ? "
            "WHERE complaint_id = ?",
            (clean_assigned_to, complaint_id),
        )
        conn.commit()
        log_audit("Complaint", "Assign", str(complaint_id), "Success",
                   f"Assigned to '{clean_assigned_to}'.")

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Complaint", "DatabaseError", "High", "assign_complaint",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not assign the complaint due to a database error.")
    finally:
        conn.close()


def resolve_complaint(complaint_id: int, resolution_notes: str) -> None:
    """Move a complaint from 'Open' or 'Assigned' to 'Resolved'."""
    clean_notes = validate_resolution_notes(resolution_notes)

    conn = get_connection()
    try:
        cur = conn.cursor()
        complaint = _get_complaint_or_raise(cur, complaint_id)

        if complaint["status"] not in _RESOLVABLE_STATUSES:
            raise ValidationError(
                f"Cannot resolve a complaint with status '{complaint['status']}'. "
                f"It may already be resolved."
            )

        resolved_at = datetime.now().isoformat(timespec="seconds")
        cur.execute(
            "UPDATE complaints SET status = 'Resolved', resolved_at = ?, "
            "resolution_notes = ? WHERE complaint_id = ?",
            (resolved_at, clean_notes, complaint_id),
        )
        conn.commit()
        log_audit("Complaint", "Resolve", str(complaint_id), "Success",
                   f"Resolved at {resolved_at}.")

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Complaint", "DatabaseError", "High", "resolve_complaint",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not resolve the complaint due to a database error.")
    finally:
        conn.close()


def get_all_complaints() -> list:
    """All complaints joined with student name, newest first."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.complaint_id, c.category, c.description, c.status,
                   c.assigned_to, c.created_at, c.resolved_at, c.resolution_notes,
                   s.student_id, s.name AS student_name
            FROM complaints c
            JOIN students s ON s.student_id = c.student_id
            ORDER BY c.complaint_id DESC
        """)
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Complaint", "DatabaseError", "Medium", "get_all_complaints",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()
