"""Audit log viewer and student data download (administrators only)."""
import csv

from app.database.db import get_connection
from app.utils import session
from app.utils import logging_service as ls
from app.utils.logging_service import _neutralise, log_audit, log_error
from app.utils.timefmt import utc_to_local
from app.utils.validation import ValidationError


def read_audit_log(search: str = "", module: str = "", limit: int = 500) -> list:
    """Newest-first audit entries, optionally filtered by module and a text search."""
    session.require_roles(session.ADMIN_ROLES, "view the audit log")
    try:
        with open(ls.AUDIT_LOG_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return []
    except (OSError, csv.Error) as exc:
        log_error("Audit", "FileError", "Medium", "read_audit_log", status="Open", message_reference=str(exc))
        raise ValidationError("The audit log could not be read.")
    needle = (search or "").strip().lower()
    result = []
    for row in reversed(rows):
        if module and row.get("module") != module:
            continue
        if needle and needle not in " ".join(str(v) for v in row.values()).lower():
            continue
        result.append(row)
        if len(result) >= int(limit):
            break
    return result


def audit_modules() -> list:
    session.require_roles(session.ADMIN_ROLES, "view the audit log")
    try:
        with open(ls.AUDIT_LOG_CSV, newline="", encoding="utf-8") as f:
            return sorted({r.get("module") for r in csv.DictReader(f) if r.get("module")})
    except (OSError, csv.Error):
        return []


def export_students_csv(path: str) -> int:
    """Write every student with gender and current room to a CSV file. Returns the row count."""
    session.require_roles(session.ADMIN_ROLES, "download student data")
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT s.student_id, s.name, s.registration_number, s.contact_number, s.gender, s.created_at, "
            "r.room_number, r.floor, r.hostel_type FROM students s "
            "LEFT JOIN allocations a ON a.student_id = s.student_id AND a.status = 'Active' "
            "LEFT JOIN rooms r ON r.room_id = a.room_id ORDER BY s.student_id").fetchall()
    finally:
        conn.close()
    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Registration No.", "Contact", "Gender", "Added On", "Room", "Floor", "Hostel"])
            for r in rows:
                writer.writerow([_neutralise(v) if v is not None else "" for v in (
                    r["student_id"], r["name"], r["registration_number"], r["contact_number"], r["gender"],
                    utc_to_local(r["created_at"]), r["room_number"], r["floor"] if r["room_number"] else None,
                    r["hostel_type"])])
    except OSError as exc:
        log_error("Student", "FileError", "Medium", "export_students_csv", status="Open", message_reference=str(exc))
        raise ValidationError("Could not write the file to that location.")
    log_audit("Student", "Export", "all", "Success", f"Downloaded {len(rows)} student record(s).")
    return len(rows)
