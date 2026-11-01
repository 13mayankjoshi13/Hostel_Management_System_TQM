"""FMEA register (editable, RPN = severity x occurrence x detection) and the SIPOC table."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit
from app.utils.validation import ValidationError, validate_record_id

RPN_ACTION_THRESHOLD = 100

_SIPOC_SEED = [
    ("Student / hostel office", "Name, registration number, contact, gender", "Student registration",
     "Student record", "Warden"),
    ("Hostel office", "Room number, type, capacity, floor, hostel", "Room set-up", "Room record", "Warden"),
    ("Student record and room record", "Student, room", "Room allocation (full room, one room per student, "
     "Boys/Girls match checked first)", "Active allocation", "Student"),
    ("Student", "Complaint category and description", "Complaint handling (assign, resolve)",
     "Resolved complaint", "Student"),
    ("Student", "Leave dates and reason", "Leave tracking", "Leave record shown as Leave in attendance", "Warden"),
    ("Warden / staff", "Daily roll call", "Attendance", "Present or Absent record", "Student, warden"),
    ("Warden", "Student, reason, amount", "Fine and online payment", "Paid fine and receipt", "Student"),
    ("Warden / staff", "Notice title and text", "Notices", "Notice in the student's My Notices", "Student"),
]


def _text(value, what, required=True, limit=200) -> str:
    value = " ".join(str(value or "").split())
    if required and not value:
        raise ValidationError(f"{what} cannot be empty.")
    if len(value) > limit:
        raise ValidationError(f"{what} must be {limit} characters or fewer.")
    return value


def _rating(value, what) -> int:
    try:
        number = int(str(value).strip())
    except ValueError:
        raise ValidationError(f"{what} must be a whole number from 1 to 10.")
    if not 1 <= number <= 10:
        raise ValidationError(f"{what} must be a whole number from 1 to 10.")
    return number


def _write(sql: str, params: tuple, what: str, detail: str):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        log_audit("Quality", what, str(cur.lastrowid or ""), "Success", detail)
        return cur
    except sqlite3.Error:
        raise ValidationError("Could not save due to a database error.")
    finally:
        conn.close()


def add_fmea(step, failure_mode, effect, cause, severity, occurrence, detection,
             controls="", action="", module="") -> int:
    session.require_roles(session.ADMIN_ROLES, "edit the FMEA")
    values = (_text(step, "Process step", limit=80), _text(failure_mode, "Failure mode"),
              _text(effect, "Effect"), _text(cause, "Cause"),
              _rating(severity, "Severity"), _rating(occurrence, "Occurrence"), _rating(detection, "Detection"),
              _text(controls, "Current controls", False), _text(action, "Recommended action", False),
              _text(module, "Module", False, 40) or None)
    return _write("INSERT INTO fmea (process_step, failure_mode, effect, cause, severity, occurrence, detection, "
                  "current_controls, recommended_action, module) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  values, "FmeaAdd", f"Added FMEA row '{values[1]}'.").lastrowid


def update_ratings(fmea_id, severity, occurrence, detection) -> None:
    session.require_roles(session.ADMIN_ROLES, "edit the FMEA")
    fmea_id = validate_record_id(fmea_id, "Select an FMEA row first.")
    cur = _write("UPDATE fmea SET severity = ?, occurrence = ?, detection = ? WHERE fmea_id = ?",
                 (_rating(severity, "Severity"), _rating(occurrence, "Occurrence"), _rating(detection, "Detection"),
                  fmea_id), "FmeaUpdate", f"Updated ratings of FMEA row {fmea_id}.")
    if cur.rowcount == 0:
        raise ValidationError("That FMEA row no longer exists.")


def delete_fmea(fmea_id) -> None:
    session.require_roles(session.ADMIN_ROLES, "edit the FMEA")
    fmea_id = validate_record_id(fmea_id, "Select an FMEA row first.")
    if _write("DELETE FROM fmea WHERE fmea_id = ?", (fmea_id,), "FmeaDelete",
              f"Deleted FMEA row {fmea_id}.").rowcount == 0:
        raise ValidationError("That FMEA row no longer exists.")


def list_fmea() -> list:
    """Rows highest RPN first, each with the number of bugs logged against its module (real evidence)."""
    session.require_roles(session.ADMIN_ROLES, "view the FMEA")
    conn = get_connection()
    try:
        bugs = dict(conn.execute("SELECT LOWER(module), COUNT(*) FROM bugs GROUP BY LOWER(module)").fetchall())
        rows = [dict(r) for r in conn.execute("SELECT * FROM fmea")]
    finally:
        conn.close()
    for row in rows:
        row["rpn"] = row["severity"] * row["occurrence"] * row["detection"]
        row["act"] = row["rpn"] >= RPN_ACTION_THRESHOLD
        row["bugs_logged"] = bugs.get((row["module"] or "").lower(), 0) if row["module"] else None
    return sorted(rows, key=lambda r: (-r["rpn"], r["fmea_id"]))


def ensure_default_sipoc() -> None:
    conn = get_connection()
    try:
        if conn.execute("SELECT COUNT(*) FROM sipoc").fetchone()[0] == 0:
            conn.executemany("INSERT INTO sipoc (supplier, input, process, output, customer) VALUES (?, ?, ?, ?, ?)",
                             _SIPOC_SEED)
            conn.commit()
    finally:
        conn.close()


def list_sipoc() -> list:
    session.require_roles(session.ADMIN_ROLES, "view the SIPOC")
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM sipoc ORDER BY sipoc_id")]
    finally:
        conn.close()


def add_sipoc(supplier, inp, process, output, customer) -> int:
    session.require_roles(session.ADMIN_ROLES, "edit the SIPOC")
    values = tuple(_text(v, label, limit=160) for v, label in (
        (supplier, "Supplier"), (inp, "Input"), (process, "Process"), (output, "Output"), (customer, "Customer")))
    return _write("INSERT INTO sipoc (supplier, input, process, output, customer) VALUES (?, ?, ?, ?, ?)",
                  values, "SipocAdd", f"Added SIPOC row '{values[2]}'.").lastrowid


def delete_sipoc(sipoc_id) -> None:
    session.require_roles(session.ADMIN_ROLES, "edit the SIPOC")
    sipoc_id = validate_record_id(sipoc_id, "Select a SIPOC row first.")
    if _write("DELETE FROM sipoc WHERE sipoc_id = ?", (sipoc_id,), "SipocDelete",
              f"Deleted SIPOC row {sipoc_id}.").rowcount == 0:
        raise ValidationError("That SIPOC row no longer exists.")
