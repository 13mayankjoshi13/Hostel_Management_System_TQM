"""Hostel timing configuration and student out/return status tracking."""
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit
from app.utils.validation import ValidationError

DEFAULT_TIMINGS = {
    "mess_breakfast": "07:30 AM – 09:30 AM",
    "mess_lunch": "12:30 PM – 02:30 PM",
    "mess_snacks": "05:00 PM – 06:00 PM",
    "mess_dinner": "07:30 PM – 09:30 PM",
    "college": "09:00 AM – 05:00 PM (Mon–Fri)",
    "outing": "05:00 PM – 08:30 PM (Daily)",
    "returning": "08:30 PM (Strict Gate In-Time)",
}

TIMING_LABELS = {
    "mess_breakfast": "Mess: Breakfast",
    "mess_lunch": "Mess: Lunch",
    "mess_snacks": "Mess: Evening Snacks",
    "mess_dinner": "Mess: Dinner",
    "college": "College Hours",
    "outing": "Outing Permitted",
    "returning": "Gate Curfew / In-Time",
}


def get_timings() -> dict:
    """Retrieve current hostel timings, falling back to defaults for any unset keys."""
    timings = dict(DEFAULT_TIMINGS)
    try:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT key, value FROM app_settings WHERE key LIKE 'timing:%'"
            ).fetchall()
            for r in rows:
                field = r["key"].split("timing:", 1)[1]
                if field in DEFAULT_TIMINGS:
                    timings[field] = r["value"]
        finally:
            conn.close()
    except sqlite3.Error:
        pass
    return timings


def save_timings(timings: dict) -> dict:
    """Save updated hostel timings. Only administrators can perform this action."""
    session.require_roles(session.ADMIN_ROLES, "edit hostel timings")
    if not isinstance(timings, dict):
        raise ValidationError("Invalid timings data format.")

    cleaned = {}
    for key, default_val in DEFAULT_TIMINGS.items():
        val = timings.get(key, default_val)
        if val is None or not str(val).strip():
            raise ValidationError(f"Timing for '{TIMING_LABELS.get(key, key)}' cannot be blank.")
        cleaned[key] = str(val).strip()

    conn = get_connection()
    try:
        cur = conn.cursor()
        for key, val in cleaned.items():
            cur.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (f"timing:{key}", val)
            )
        conn.commit()
        log_audit("Settings", "UpdateTimings", "hostel_timings", "Success", "Hostel schedule and timings updated.")
    finally:
        conn.close()

    return cleaned


def get_student_return_status(student_id: int = None) -> dict:
    """Check if a hosteller is currently out on leave/outing and get returning expectations."""
    if student_id is None:
        student_id = session.get_student_id()

    timings = get_timings()
    gate_curfew = timings.get("returning", "08:30 PM (Gate In-Time)")

    if not student_id:
        return {
            "is_out": False,
            "badge": "IN HOSTEL",
            "status": "In Hostel",
            "returning_info": f"Curfew: {gate_curfew}",
            "details": f"Present in campus. Daily return curfew is {gate_curfew}.",
        }

    try:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT leave_id, from_date, to_date, reason, status FROM leaves "
                "WHERE student_id = ? AND status = 'On Leave' "
                "ORDER BY leave_id DESC LIMIT 1",
                (student_id,)
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        row = None

    if row:
        return {
            "is_out": True,
            "badge": "OUT ON LEAVE",
            "status": "On Leave",
            "leave_id": row["leave_id"],
            "from_date": row["from_date"],
            "to_date": row["to_date"],
            "reason": row["reason"],
            "returning_info": f"Expected Return: {row['to_date']}",
            "details": f"Hosteller is out on approved leave ({row['from_date']} to {row['to_date']}). Reason: {row['reason']}. Check-in must be recorded by Warden/Admin upon return.",
        }

    return {
        "is_out": False,
        "badge": "IN HOSTEL",
        "status": "In Hostel",
        "leave_id": None,
        "from_date": None,
        "to_date": None,
        "reason": None,
        "returning_info": f"Gate Curfew: {gate_curfew}",
        "details": f"Present in campus. Daily return curfew is {gate_curfew}.",
    }
