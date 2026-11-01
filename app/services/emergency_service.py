"""Emergency numbers. Only the national numbers are pre-filled; add your university's own."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit
from app.utils.validation import (
    ValidationError, validate_contact_label, validate_emergency_number, validate_record_id,
)

DEFAULT_CONTACTS = [
    ("National Emergency", "112", "National"),
    ("Police", "100", "National"),
    ("Fire", "101", "National"),
    ("Ambulance", "108", "National"),
    ("Women Helpline", "1091", "National"),
]


def seed_defaults() -> None:
    conn = get_connection()
    try:
        if conn.execute("SELECT COUNT(*) FROM emergency_contacts").fetchone()[0] == 0:
            conn.executemany("INSERT INTO emergency_contacts (name, number, category) VALUES (?, ?, ?)",
                             DEFAULT_CONTACTS)
            conn.commit()
    finally:
        conn.close()


def list_contacts() -> list:
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM emergency_contacts ORDER BY category = 'National', category, contact_id").fetchall()]
    finally:
        conn.close()


def add_contact(name: str, number: str, category: str = "University") -> int:
    session.require_roles(session.ADMIN_ROLES, "edit emergency numbers")
    clean_name = validate_contact_label(name)
    clean_number = validate_emergency_number(number)
    clean_category = validate_contact_label(category, "Category")
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO emergency_contacts (name, number, category) VALUES (?, ?, ?)",
                           (clean_name, clean_number, clean_category))
        conn.commit()
        log_audit("Emergency", "Create", str(cur.lastrowid), "Success", f"Added '{clean_name}'.")
        return cur.lastrowid
    except sqlite3.Error:
        raise ValidationError("Could not save the number due to a database error.")
    finally:
        conn.close()


def delete_contact(contact_id: int) -> None:
    session.require_roles(session.ADMIN_ROLES, "edit emergency numbers")
    contact_id = validate_record_id(contact_id, "Select a number first.")
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM emergency_contacts WHERE contact_id = ?", (contact_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValidationError("That number no longer exists.")
        log_audit("Emergency", "Delete", str(contact_id), "Success", "Emergency number removed.")
    finally:
        conn.close()
