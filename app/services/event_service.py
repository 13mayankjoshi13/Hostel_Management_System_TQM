"""
Calendar events: holidays, hostel events and exams.

Anyone logged in can read; only Administrators and Wardens can add or
delete. Default holidays are the 2026 Central Government list (checked
12/10/2026 against bankbazaar.com) — compare with your university's own
calendar and edit in the Calendar screen.
"""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_error, log_audit
from app.utils.validation import (validate_event_date, validate_event_title,
                                    validate_event_kind, ValidationError)

_EDITOR_ROLES = {"Administrator", "Warden"}

DEFAULT_HOLIDAYS = [
    ("2026-01-14", "Makar Sankranti"), ("2026-01-23", "Parakram Divas"),
    ("2026-01-26", "Republic Day"), ("2026-03-03", "Holi"), ("2026-03-21", "Eid-ul-Fitr"),
    ("2026-03-26", "Ram Navami"), ("2026-03-31", "Mahavir Jayanti"), ("2026-04-03", "Good Friday"),
    ("2026-04-14", "Dr Ambedkar Jayanti"), ("2026-05-01", "Buddha Purnima"),
    ("2026-05-27", "Bakrid / Eid al-Adha"), ("2026-06-26", "Muharram"),
    ("2026-08-15", "Independence Day"), ("2026-08-25", "Eid-e-Milad"),
    ("2026-08-28", "Raksha Bandhan"), ("2026-09-04", "Janmashtami"),
    ("2026-10-02", "Gandhi Jayanti"), ("2026-10-20", "Dussehra"), ("2026-11-08", "Diwali"),
    ("2026-11-09", "Govardhan Puja"), ("2026-11-11", "Bhai Dooj"),
    ("2026-11-24", "Guru Nanak Jayanti"), ("2026-12-25", "Christmas"),
]


def _require_editor() -> None:
    if session.get_role() not in _EDITOR_ROLES:
        raise ValidationError("Only an Administrator or Warden can change calendar events.")


def add_event(event_date: str, title: str, kind: str) -> int:
    _require_editor()
    clean_date = validate_event_date(event_date)
    clean_title = validate_event_title(title)
    clean_kind = validate_event_kind(kind)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT event_id FROM events WHERE event_date = ? AND title = ?", (clean_date, clean_title))
        if cur.fetchone() is not None:
            raise ValidationError("That event already exists on this date.")
        cur.execute("INSERT INTO events (event_date, title, kind) VALUES (?, ?, ?)",
                    (clean_date, clean_title, clean_kind))
        conn.commit()
        event_id = cur.lastrowid
        log_audit("Calendar", "Create", str(event_id), "Success",
                   f"Added {clean_kind} '{clean_title}' on {clean_date}.")
        return event_id
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Calendar", "DatabaseError", "Medium", "add_event",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the event due to a database error.")
    finally:
        conn.close()


def delete_event(event_id: int) -> None:
    _require_editor()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT title FROM events WHERE event_id = ?", (event_id,))
        row = cur.fetchone()
        if row is None:
            raise ValidationError("That event does not exist.")
        cur.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
        conn.commit()
        log_audit("Calendar", "Delete", str(event_id), "Success", f"Deleted event '{row['title']}'.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Calendar", "DatabaseError", "Medium", "delete_event",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not delete the event due to a database error.")
    finally:
        conn.close()


def _query(sql: str, params: tuple, action: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Calendar", "DatabaseError", "Low", action, status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def get_events_for_month(year: int, month: int) -> list:
    prefix = f"{int(year):04d}-{int(month):02d}-"
    return _query("SELECT * FROM events WHERE event_date LIKE ? ORDER BY event_date, title",
                  (prefix + "%",), "get_events_for_month")


def get_upcoming(from_date: str, limit: int = 5) -> list:
    return _query("SELECT * FROM events WHERE event_date >= ? ORDER BY event_date, title LIMIT ?",
                  (from_date, limit), "get_upcoming")


def get_all_events() -> list:
    return _query("SELECT * FROM events ORDER BY event_date, title", (), "get_all_events")


def ensure_default_holidays() -> None:
    """First-run: load the default holidays if no Holiday exists yet."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM events WHERE kind = 'Holiday'")
        if cur.fetchone()["n"] > 0:
            return
        cur.executemany("INSERT OR IGNORE INTO events (event_date, title, kind) VALUES (?, ?, 'Holiday')",
                        DEFAULT_HOLIDAYS)
        conn.commit()
        log_audit("Calendar", "Seed", "defaults", "Success",
                   f"Loaded {len(DEFAULT_HOLIDAYS)} default 2026 holidays.")
    except sqlite3.Error as exc:
        log_error("Calendar", "DatabaseError", "Low", "ensure_default_holidays",
                   status="Open", message_reference=str(exc))
    finally:
        conn.close()
