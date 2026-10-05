"""
Bug Tracker service (Q09 feature #4).

Fields match the project's assigned spec exactly: Bug ID, Date, Module,
Category, Title, Description, Severity, Priority, Status, Root Cause,
Corrective Action, Test Case.

Status pipeline (forward-only, same prevention-at-source pattern as
allocations and complaints):

    Open  --start_progress-->  In Progress  --mark_fixed-->  Fixed  --close_bug--> Closed

A bug can't skip steps, can't move backward, and "Fixed" requires a
documented root cause, corrective action, and test case reference before
it's accepted — you can't mark something fixed without saying how. Every
create and status change writes a REAL row to TQM/data/defect_log.csv
via log_defect(); nothing here fabricates a resolution.
"""
import sqlite3
from datetime import date as date_cls

from app.database.db import get_connection
from app.utils.validation import (
    validate_bug_module, validate_bug_category, validate_bug_title,
    validate_bug_description, validate_severity, validate_priority,
    validate_root_cause, validate_corrective_action, validate_test_case,
    ValidationError,
)
from app.utils.logging_service import log_error, log_audit, log_defect

def _defect_id(bug_id: int) -> str:
    return f"BUG-{bug_id:04d}"


def _get_bug_or_raise(cur, bug_id: int) -> sqlite3.Row:
    cur.execute("SELECT * FROM bugs WHERE bug_id = ?", (bug_id,))
    bug = cur.fetchone()
    if bug is None:
        raise ValidationError(f"No bug found with ID {bug_id}.")
    return bug


def log_bug(module: str, category: str, title: str, description: str,
            severity: str, priority: str) -> int:
    """Validate and insert a new bug with status 'Open'. Returns the new bug_id."""
    clean_module = validate_bug_module(module)
    clean_category = validate_bug_category(category)
    clean_title = validate_bug_title(title)
    clean_description = validate_bug_description(description)
    clean_severity = validate_severity(severity)
    clean_priority = validate_priority(priority)
    today = date_cls.today().isoformat()

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bugs (date, module, category, title, description, "
            "severity, priority, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Open')",
            (today, clean_module, clean_category, clean_title, clean_description,
             clean_severity, clean_priority),
        )
        conn.commit()
        bug_id = cur.lastrowid

        log_defect(_defect_id(bug_id), today, clean_module, clean_category, clean_title,
                   clean_description, clean_severity, clean_priority, "Open")
        log_audit("Bug", "Create", str(bug_id), "Success",
                   f"Logged bug '{clean_title}' ({clean_severity}/{clean_priority}).")
        return bug_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Bug", "DatabaseError", "High", "log_bug",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the bug due to a database error.")
    finally:
        conn.close()


def start_progress(bug_id: int) -> None:
    """Move a bug from 'Open' to 'In Progress'."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        bug = _get_bug_or_raise(cur, bug_id)
        if bug["status"] != "Open":
            raise ValidationError(
                f"Cannot start progress on a bug with status '{bug['status']}'. "
                f"Only 'Open' bugs can move to 'In Progress'."
            )
        cur.execute("UPDATE bugs SET status = 'In Progress' WHERE bug_id = ?", (bug_id,))
        conn.commit()

        log_defect(_defect_id(bug_id), bug["date"], bug["module"], bug["category"], bug["title"],
                   bug["description"], bug["severity"], bug["priority"], "In Progress")
        log_audit("Bug", "StartProgress", str(bug_id), "Success", "Moved to In Progress.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Bug", "DatabaseError", "High", "start_progress",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the bug due to a database error.")
    finally:
        conn.close()


def mark_fixed(bug_id: int, root_cause: str, corrective_action: str, test_case: str) -> None:
    """Move a bug from 'In Progress' to 'Fixed'. Requires full documentation."""
    clean_root_cause = validate_root_cause(root_cause)
    clean_corrective_action = validate_corrective_action(corrective_action)
    clean_test_case = validate_test_case(test_case)

    conn = get_connection()
    try:
        cur = conn.cursor()
        bug = _get_bug_or_raise(cur, bug_id)
        if bug["status"] != "In Progress":
            raise ValidationError(
                f"Cannot mark fixed a bug with status '{bug['status']}'. "
                f"It must be 'In Progress' first."
            )
        cur.execute(
            "UPDATE bugs SET status = 'Fixed', root_cause = ?, corrective_action = ?, "
            "test_case = ? WHERE bug_id = ?",
            (clean_root_cause, clean_corrective_action, clean_test_case, bug_id),
        )
        conn.commit()

        log_defect(_defect_id(bug_id), bug["date"], bug["module"], bug["category"], bug["title"],
                   bug["description"], bug["severity"], bug["priority"], "Fixed",
                   clean_root_cause, clean_corrective_action, clean_test_case)
        log_audit("Bug", "MarkFixed", str(bug_id), "Success",
                   f"Fixed. Root cause: {clean_root_cause[:60]}")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Bug", "DatabaseError", "High", "mark_fixed",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the bug due to a database error.")
    finally:
        conn.close()


def close_bug(bug_id: int) -> None:
    """Move a bug from 'Fixed' to 'Closed' (verified and done)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        bug = _get_bug_or_raise(cur, bug_id)
        if bug["status"] != "Fixed":
            raise ValidationError(
                f"Cannot close a bug with status '{bug['status']}'. "
                f"It must be 'Fixed' first."
            )
        cur.execute("UPDATE bugs SET status = 'Closed' WHERE bug_id = ?", (bug_id,))
        conn.commit()

        log_defect(_defect_id(bug_id), bug["date"], bug["module"], bug["category"], bug["title"],
                   bug["description"], bug["severity"], bug["priority"], "Closed",
                   bug["root_cause"] or "", bug["corrective_action"] or "", bug["test_case"] or "")
        log_audit("Bug", "Close", str(bug_id), "Success", "Closed.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Bug", "DatabaseError", "High", "close_bug",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the bug due to a database error.")
    finally:
        conn.close()


def get_all_bugs() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bugs ORDER BY bug_id DESC")
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Bug", "DatabaseError", "Medium", "get_all_bugs",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()
