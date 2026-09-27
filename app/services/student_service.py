"""
Student Management service.

Every public function follows the same TQM error-prevention pipeline:

    Raw Input -> Strict Validation -> Business Rule Check -> Database
                                            |
                                   (failure at any stage is
                                    logged and re-raised as a
                                    clean, user-facing message)
"""
import sqlite3

from app.database.db import get_connection
from app.utils.validation import (
    validate_student_name,
    validate_registration_number,
    validate_contact_number,
    ValidationError,
)
from app.utils.logging_service import log_error, log_audit


def add_student(name: str, registration_number: str, contact_number: str) -> int:
    """
    Validate and insert a new student. Returns the new student_id.
    Raises ValidationError for any rejected input (duplicate registration
    number included) — the UI is expected to catch this and show it
    directly to the user.
    """
    clean_name = validate_student_name(name)
    clean_reg_no = validate_registration_number(registration_number)
    clean_contact = validate_contact_number(contact_number)

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Explicit duplicate check first, so we can give a specific
        # message rather than a generic database integrity error.
        cur.execute(
            "SELECT student_id FROM students WHERE registration_number = ?",
            (clean_reg_no,),
        )
        if cur.fetchone() is not None:
            raise ValidationError(
                f"A student with registration number '{clean_reg_no}' already exists."
            )

        cur.execute(
            "INSERT INTO students (name, registration_number, contact_number) "
            "VALUES (?, ?, ?)",
            (clean_name, clean_reg_no, clean_contact),
        )
        conn.commit()
        student_id = cur.lastrowid
        log_audit("Student", "Create", str(student_id), "Success",
                   f"Registered student '{clean_name}' ({clean_reg_no}).")
        return student_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "High", "add_student",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the student due to a database error.")
    finally:
        conn.close()


def get_all_students() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students ORDER BY student_id DESC")
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "Medium", "get_all_students",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        log_audit("Student", "Delete", str(student_id), "Success",
                   "Student record deleted.")
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "High", "delete_student",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not delete the student due to a database error.")
    finally:
        conn.close()
