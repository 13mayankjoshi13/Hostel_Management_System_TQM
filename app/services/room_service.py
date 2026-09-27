"""
Room Management service. Same error-prevention pipeline as student_service.
"""
import sqlite3

from app.database.db import get_connection
from app.utils.validation import (
    validate_room_number,
    validate_room_type,
    validate_capacity,
    ValidationError,
)
from app.utils.logging_service import log_error, log_audit


def add_room(room_number: str, room_type: str, capacity) -> int:
    clean_room_no = validate_room_number(room_number)
    clean_type = validate_room_type(room_type)
    clean_capacity = validate_capacity(capacity)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT room_id FROM rooms WHERE room_number = ?", (clean_room_no,))
        if cur.fetchone() is not None:
            raise ValidationError(f"Room '{clean_room_no}' already exists.")

        cur.execute(
            "INSERT INTO rooms (room_number, room_type, capacity) VALUES (?, ?, ?)",
            (clean_room_no, clean_type, clean_capacity),
        )
        conn.commit()
        room_id = cur.lastrowid
        log_audit("Room", "Create", str(room_id), "Success",
                   f"Created room '{clean_room_no}' (capacity {clean_capacity}).")
        return room_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Room", "DatabaseError", "High", "add_room",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the room due to a database error.")
    finally:
        conn.close()


def get_all_rooms() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM rooms ORDER BY room_id DESC")
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Room", "DatabaseError", "Medium", "get_all_rooms",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def delete_room(room_id: int) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
        conn.commit()
        log_audit("Room", "Delete", str(room_id), "Success", "Room record deleted.")
    except sqlite3.Error as exc:
        log_error("Room", "DatabaseError", "High", "delete_room",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not delete the room due to a database error.")
    finally:
        conn.close()
