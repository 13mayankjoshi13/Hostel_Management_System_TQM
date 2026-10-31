"""Hostel workers (cleaners, electricians, plumbers, security...): registry, daily attendance and workload."""
import sqlite3
from datetime import date

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.validation import (ValidationError, validate_contact_number, validate_record_id,
                                  validate_worker_name, validate_worker_trade)

ATTENDANCE_STATUSES = ("Present", "Absent", "On Leave")


def _staff(action: str, roles=None) -> None:
    session.require_roles(roles or session.STAFF_ROLES, action)


def add_worker(name: str, trade: str, contact_number: str) -> int:
    _staff("add workers", session.ADMIN_ROLES)
    clean_name = validate_worker_name(name)
    clean_trade = validate_worker_trade(trade)
    clean_contact = validate_contact_number(contact_number)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM workers WHERE LOWER(name) = LOWER(?) AND contact_number = ?",
                    (clean_name, clean_contact))
        if cur.fetchone() is not None:
            raise ValidationError("A worker with this name and contact number already exists.")
        cur.execute("INSERT INTO workers (name, trade, contact_number) VALUES (?, ?, ?)",
                    (clean_name, clean_trade, clean_contact))
        conn.commit()
        log_audit("Worker", "Create", str(cur.lastrowid), "Success", f"Added {clean_trade} '{clean_name}'.")
        return cur.lastrowid
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Worker", "DatabaseError", "High", "add_worker", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the worker due to a database error.")
    finally:
        conn.close()


def set_worker_active(worker_id: int, active: bool) -> None:
    _staff("change worker status", session.ADMIN_ROLES)
    worker_id = validate_record_id(worker_id, "Please select a valid worker.")
    status = "Active" if active else "Inactive"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE workers SET status = ? WHERE worker_id = ?", (status, worker_id))
        if cur.rowcount != 1:
            raise ValidationError("That worker does not exist.")
        conn.commit()
        log_audit("Worker", "SetStatus", str(worker_id), "Success", f"Worker marked {status}.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Worker", "DatabaseError", "High", "set_worker_active", status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the worker due to a database error.")
    finally:
        conn.close()


def mark_attendance(worker_id: int, status: str, work_date: str = None) -> None:
    """One record per worker per day; marking again the same day replaces it. Today or the last 7 days only."""
    _staff("mark worker attendance")
    worker_id = validate_record_id(worker_id, "Please select a valid worker.")
    if status not in ATTENDANCE_STATUSES:
        raise ValidationError(f"Attendance must be one of: {', '.join(ATTENDANCE_STATUSES)}.")
    try:
        day = date.fromisoformat(work_date) if work_date else date.today()
    except (TypeError, ValueError):
        raise ValidationError("Attendance date must be in YYYY-MM-DD format.")
    if day > date.today() or (date.today() - day).days > 7:
        raise ValidationError("Attendance can be recorded for today or the past 7 days only.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT status FROM workers WHERE worker_id = ?", (worker_id,))
        worker = cur.fetchone()
        if worker is None:
            raise ValidationError("That worker does not exist.")
        if worker["status"] != "Active":
            raise ValidationError("Attendance cannot be marked for an inactive worker.")
        cur.execute("INSERT INTO worker_attendance (worker_id, work_date, status) VALUES (?, ?, ?) "
                    "ON CONFLICT(worker_id, work_date) DO UPDATE SET status = excluded.status",
                    (worker_id, day.isoformat(), status))
        conn.commit()
        log_audit("Worker", "Attendance", str(worker_id), "Success", f"{status} on {day.isoformat()}.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Worker", "DatabaseError", "High", "mark_attendance", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save attendance due to a database error.")
    finally:
        conn.close()


def get_workers(active_only: bool = False) -> list:
    """Workers with today's attendance and complaint workload (open = assigned, resolved = completed)."""
    _staff("view workers")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT w.worker_id, w.name, w.trade, w.contact_number, w.status,
                   COALESCE(a.status, 'Not marked') AS today,
                   (SELECT COUNT(*) FROM complaints c WHERE c.assigned_to = w.name AND c.status = 'Assigned') AS open_jobs,
                   (SELECT COUNT(*) FROM complaints c WHERE c.assigned_to = w.name AND c.status = 'Resolved') AS done_jobs
            FROM workers w
            LEFT JOIN worker_attendance a ON a.worker_id = w.worker_id AND a.work_date = ?
            WHERE (? = 0 OR w.status = 'Active')
            ORDER BY w.name COLLATE NOCASE
        """, (date.today().isoformat(), int(active_only)))
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Worker", "DatabaseError", "Medium", "get_workers", status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()
