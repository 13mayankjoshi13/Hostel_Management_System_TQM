"""Gate log: security records students going out and coming in; late entries are flagged."""
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.timefmt import localise_rows, utc_now
from app.utils.validation import ValidationError, validate_record_id

CURFEW_HOUR = 22
EARLIEST_HOUR = 5


def _is_late(local_stamp: str) -> bool:
    hour = datetime.fromisoformat(local_stamp).hour
    return hour >= CURFEW_HOUR or hour < EARLIEST_HOUR


def _is_out(conn, student_id: int) -> bool:
    row = conn.execute("SELECT direction FROM gate_log WHERE student_id = ? ORDER BY gate_id DESC LIMIT 1",
                       (student_id,)).fetchone()
    return bool(row) and row["direction"] == "Out"


def log_movement(student_id: int, direction: str) -> int:
    session.require_roles(session.GATE_ROLES, "log gate movements")
    student_id = validate_record_id(student_id, "Select a student first.")
    if direction not in ("In", "Out"):
        raise ValidationError("Direction must be In or Out.")
    conn = get_connection()
    try:
        if conn.execute("SELECT 1 FROM allocations WHERE student_id = ? AND status = 'Active'",
                        (student_id,)).fetchone() is None:
            raise ValidationError("This student has no active room.")
        out_now = _is_out(conn, student_id)
        if direction == "Out" and out_now:
            raise ValidationError("This student is already marked as out.")
        if direction == "In" and not out_now:
            raise ValidationError("This student is not marked as out.")
        now = utc_now()
        local = localise_rows([{"t": now}], "t")[0]["t"]
        late = 1 if direction == "In" and _is_late(local) else 0
        cur = conn.execute("INSERT INTO gate_log (student_id, direction, logged_at, late, logged_by) VALUES (?, ?, ?, ?, ?)",
                           (student_id, direction, now, late, session.get_user()))
        conn.commit()
        log_audit("Gate", direction, str(student_id), "Success", "Late entry." if late else f"Marked {direction}.")
        return cur.lastrowid
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Gate", "DatabaseError", "High", "log_movement", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the entry due to a database error.")
    finally:
        conn.close()


def students_for_gate() -> list:
    session.require_roles(session.GATE_ROLES, "view students with rooms")
    conn = get_connection()
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT s.student_id, s.name AS student_name, r.room_number FROM allocations al "
            "JOIN students s ON s.student_id = al.student_id JOIN rooms r ON r.room_id = al.room_id "
            "WHERE al.status = 'Active' ORDER BY s.name")]
        for row in rows:
            row["is_out"] = _is_out(conn, row["student_id"])
        return rows
    finally:
        conn.close()


def list_log(limit: int = 200, late_only: bool = False) -> list:
    session.require_roles(session.GATE_ROLES, "view the gate log")
    sql = ("SELECT g.gate_id, s.name AS student_name, r.room_number, g.direction, g.logged_at, g.late "
           "FROM gate_log g JOIN students s ON s.student_id = g.student_id "
           "LEFT JOIN allocations al ON al.student_id = g.student_id AND al.status = 'Active' "
           "LEFT JOIN rooms r ON r.room_id = al.room_id ")
    if late_only:
        sql += "WHERE g.late = 1 "
    conn = get_connection()
    try:
        rows = [dict(r) for r in conn.execute(sql + "ORDER BY g.gate_id DESC LIMIT ?", (int(limit),))]
    finally:
        conn.close()
    for row in localise_rows(rows, "logged_at"):
        row["room_number"] = row["room_number"] or "-"
    return rows


def counts() -> dict:
    session.require_roles(session.GATE_ROLES, "view the gate log")
    conn = get_connection()
    try:
        out_now = sum(1 for r in conn.execute("SELECT DISTINCT student_id FROM gate_log")
                      if _is_out(conn, r["student_id"]))
        late = [r["logged_at"] for r in conn.execute("SELECT logged_at FROM gate_log WHERE late = 1")]
    finally:
        conn.close()
    today = datetime.now().date().isoformat()
    late_today = sum(1 for t in localise_rows([{"t": x} for x in late], "t") if t["t"][:10] == today)
    return {"out_now": out_now, "late_today": late_today, "late_total": len(late)}
