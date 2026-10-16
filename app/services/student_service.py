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
from app.utils import session
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


SORT_OPTIONS = {
    "Newest first": ("student_id", True),
    "Oldest first": ("student_id", False),
    "Name A-Z": ("name", False),
    "Name Z-A": ("name", True),
    "Registration No.": ("registration_number", False),
}


def get_all_students(sort_by: str = "Newest first") -> list:
    if sort_by not in SORT_OPTIONS:
        sort_by = "Newest first"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        rows = [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "Medium", "get_all_students",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()
    column, reverse = SORT_OPTIONS[sort_by]
    key = (lambda r: r[column].lower()) if column == "name" else (lambda r: r[column])
    return sorted(rows, key=key, reverse=reverse)


def update_student(student_id: int, name: str, registration_number: str, contact_number: str) -> None:
    """Edit a student's details. Staff roles only; students use student_portal_service."""
    if session.get_role() == "Student":
        raise ValidationError("Students can only edit their own details from My Details.")
    _update(student_id, name, registration_number, contact_number)


def _update(student_id: int, name: str, registration_number: str, contact_number: str) -> None:
    clean_name = validate_student_name(name)
    clean_reg_no = validate_registration_number(registration_number)
    clean_contact = validate_contact_number(contact_number)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        old = cur.fetchone()
        if old is None:
            raise ValidationError("That student does not exist.")
        cur.execute("SELECT student_id FROM students WHERE registration_number = ? AND student_id != ?",
                    (clean_reg_no, student_id))
        if cur.fetchone() is not None:
            raise ValidationError(f"A student with registration number '{clean_reg_no}' already exists.")
        cur.execute("UPDATE students SET name = ?, registration_number = ?, contact_number = ? "
                    "WHERE student_id = ?", (clean_name, clean_reg_no, clean_contact, student_id))
        conn.commit()
        changed = [label for label, before, after in (
            ("name", old["name"], clean_name),
            ("registration number", old["registration_number"], clean_reg_no),
            ("contact", old["contact_number"], clean_contact)) if before != after]
        log_audit("Student", "Update", str(student_id), "Success",
                   "Changed " + (", ".join(changed) if changed else "nothing") + ".")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "High", "update_student",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the student due to a database error.")
    finally:
        conn.close()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
        student = cur.fetchone()
        if student is None:
            raise ValidationError("That student does not exist.")
        cur.execute("SELECT COUNT(*) AS n FROM allocations WHERE student_id = ? AND status = 'Active'", (student_id,))
        if cur.fetchone()["n"]:
            raise ValidationError(f"{student['name']} has an active room allocation. Release it first.")
        for table, what in (("allocations", "allocation"), ("complaints", "complaint"),
                            ("leaves", "leave"), ("users", "login account")):
            cur.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE student_id = ?", (student_id,))
            if cur.fetchone()["n"]:
                raise ValidationError(f"{student['name']} has {what} records, so the student cannot be deleted.")
        cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        log_audit("Student", "Delete", str(student_id), "Success",
                   "Student record deleted.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Student", "DatabaseError", "High", "delete_student",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not delete the student due to a database error.")
    finally:
        conn.close()
