"""Housekeeping: a daily cleaning checklist for every hostel floor."""
import sqlite3
from datetime import date

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.timefmt import utc_now
from app.utils.validation import ValidationError

AREAS = ("Corridor", "Washrooms", "Common room", "Stairs")


def _floors(conn) -> list:
    rows = conn.execute("SELECT DISTINCT COALESCE(hostel_type, 'Unassigned') AS hostel, floor FROM rooms "
                        "ORDER BY hostel, floor").fetchall()
    return [(r["hostel"], r["floor"]) for r in rows]


def checklist(day: str = None) -> list:
    session.require_roles(session.CLEANING_VIEW_ROLES, "view the cleaning checklist")
    day = day or date.today().isoformat()
    conn = get_connection()
    try:
        done = {(r["hostel"], r["floor"], r["area"]): r["done_by"] for r in conn.execute(
            "SELECT hostel, floor, area, done_by FROM cleaning_checks WHERE check_date = ?", (day,))}
        out = []
        for hostel, floor in _floors(conn):
            areas = {a: done.get((hostel, floor, a)) for a in AREAS}
            out.append({"hostel": hostel, "floor": floor, "areas": areas,
                        "done": sum(1 for v in areas.values() if v), "total": len(AREAS)})
        return out
    finally:
        conn.close()


def set_done(hostel: str, floor: int, area: str, done: bool = True) -> None:
    """Mark an area clean (or undo it) for today."""
    session.require_roles(session.CLEANING_MANAGE_ROLES, "update the cleaning checklist")
    if area not in AREAS:
        raise ValidationError("Choose an area to update.")
    day = date.today().isoformat()
    conn = get_connection()
    try:
        if (hostel, int(floor)) not in _floors(conn):
            raise ValidationError("That hostel floor does not exist.")
        if done:
            conn.execute("INSERT OR REPLACE INTO cleaning_checks (check_date, hostel, floor, area, done_by, done_at) "
                         "VALUES (?, ?, ?, ?, ?, ?)", (day, hostel, int(floor), area, session.get_user(), utc_now()))
        else:
            conn.execute("DELETE FROM cleaning_checks WHERE check_date = ? AND hostel = ? AND floor = ? AND area = ?",
                         (day, hostel, int(floor), area))
        conn.commit()
        log_audit("Cleaning", "Done" if done else "Undo", f"{hostel} {floor} {area}", "Success", f"{area} on {day}.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Cleaning", "DatabaseError", "High", "set_done", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the checklist due to a database error.")
    finally:
        conn.close()


def progress(day: str = None) -> dict:
    rows = checklist(day)
    total = sum(r["total"] for r in rows)
    done = sum(r["done"] for r in rows)
    return {"done": done, "total": total, "percent": round(done / total * 100) if total else 0}
