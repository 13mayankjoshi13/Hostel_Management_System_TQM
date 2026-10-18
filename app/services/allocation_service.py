"""
Room Allocation service.

Implements the exact prevention pipeline from the project's TQM plan
(section 6, Error Prevention at Source):

    Select Student
         |
    Check Student (exists)
         |
    Select Room
         |
    Check Room Exists
         |
    Check Capacity (active allocations < room capacity)
         |
    Check Existing Allocation (student not already actively allocated)
         |
    Allocate
         |
    Audit the action

Every stage that fails raises ValidationError with a specific, user-facing
message BEFORE any row is written — this is Poka-Yoke (error prevention),
not error correction after the fact.
"""
import csv
import re
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils.validation import ValidationError, validate_record_id
from app.utils import session
from app.utils.logging_service import log_error, log_audit


def _check_student_exists(cur, student_id: int) -> sqlite3.Row:
    cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cur.fetchone()
    if student is None:
        raise ValidationError(f"No student found with ID {student_id}.")
    return student


def _check_room_exists(cur, room_id: int) -> sqlite3.Row:
    cur.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
    room = cur.fetchone()
    if room is None:
        raise ValidationError(f"No room found with ID {room_id}.")
    return room


def _check_capacity(cur, room: sqlite3.Row) -> None:
    cur.execute(
        "SELECT COUNT(*) AS active_count FROM allocations "
        "WHERE room_id = ? AND status = 'Active'",
        (room["room_id"],),
    )
    active_count = cur.fetchone()["active_count"]
    if active_count >= room["capacity"]:
        raise ValidationError(
            f"Room '{room['room_number']}' is at full capacity "
            f"({active_count}/{room['capacity']})."
        )


def _check_existing_allocation(cur, student_id: int) -> None:
    cur.execute(
        "SELECT allocation_id FROM allocations "
        "WHERE student_id = ? AND status = 'Active'",
        (student_id,),
    )
    if cur.fetchone() is not None:
        raise ValidationError(
            "This student already has an active room allocation. "
            "Release the existing allocation before allocating a new room."
        )


def allocate_room(student_id: int, room_id: int) -> int:
    """
    Run the full prevention pipeline and, if every check passes, create
    the allocation. Returns the new allocation_id.
    Raises ValidationError with a specific message on any failed check.
    """
    session.require_roles(session.STAFF_ROLES, "allocate rooms")
    student_id = validate_record_id(student_id, "Please select a student and a room.")
    room_id = validate_record_id(room_id, "Please select a student and a room.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE")

        student = _check_student_exists(cur, student_id)
        room = _check_room_exists(cur, room_id)
        _check_capacity(cur, room)
        _check_existing_allocation(cur, student_id)

        cur.execute(
            "INSERT INTO allocations (student_id, room_id, status) "
            "VALUES (?, ?, 'Active')",
            (student_id, room_id),
        )
        conn.commit()
        allocation_id = cur.lastrowid

        log_audit(
            "Allocation", "Create", str(allocation_id), "Success",
            f"Allocated student '{student['name']}' to room "
            f"'{room['room_number']}'.",
        )
        return allocation_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Allocation", "DatabaseError", "High", "allocate_room",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not create the allocation due to a database error.")
    finally:
        conn.close()


def release_allocation(allocation_id: int) -> None:
    """Mark an allocation as Released (frees the room, keeps history)."""
    session.require_roles(session.STAFF_ROLES, "release rooms")
    allocation_id = validate_record_id(allocation_id, "Please select a valid allocation.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM allocations WHERE allocation_id = ?", (allocation_id,)
        )
        allocation = cur.fetchone()
        if allocation is None:
            raise ValidationError(f"No allocation found with ID {allocation_id}.")
        if allocation["status"] != "Active":
            raise ValidationError("This allocation is not currently active.")

        cur.execute(
            "UPDATE allocations SET status = 'Released' WHERE allocation_id = ?",
            (allocation_id,),
        )
        cur.execute(
            "UPDATE leaves SET status = 'Returned', returned_at = ? "
            "WHERE student_id = ? AND status = 'On Leave'",
            (datetime.now().isoformat(timespec="seconds"), allocation["student_id"]),
        )
        conn.commit()
        log_audit("Allocation", "Release", str(allocation_id), "Success",
                   "Allocation released; room freed for reallocation.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Allocation", "DatabaseError", "High", "release_allocation",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not release the allocation due to a database error.")
    finally:
        conn.close()


def get_active_allocations() -> list:
    """Active allocations joined with student name and room number, for display."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.allocation_id, a.allocated_at, a.status,
                   s.student_id, s.name AS student_name,
                   r.room_id, r.room_number, r.room_type
            FROM allocations a
            JOIN students s ON s.student_id = a.student_id
            JOIN rooms r ON r.room_id = a.room_id
            WHERE a.status = 'Active'
            ORDER BY a.allocation_id DESC
        """)
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Allocation", "DatabaseError", "Medium", "get_active_allocations",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def _room_order(room_number: str) -> tuple:
    letters, digits = re.match(r"([^\d]*)(\d*)", room_number).groups()
    return letters.upper(), int(digits or 0), room_number


def export_allocation_list(path: str) -> int:
    """Write the active room allotment list to a CSV file. Returns the row count."""
    rows = get_active_allocations()
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Room", "Type", "Student", "Allocated At"])
            for r in sorted(rows, key=lambda r: _room_order(r["room_number"])):
                writer.writerow([r["room_number"], r["room_type"], r["student_name"], r["allocated_at"]])
    except OSError as exc:
        log_error("Allocation", "FileError", "Medium", "export_allocation_list",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not write the allotment list to that location.")
    log_audit("Allocation", "Export", "list", "Success", f"Exported {len(rows)} allocation(s).")
    return len(rows)
