"""
Error Logs + Audit Logs (Q09 feature #5 and TQM traceability).

This module is the ONLY place that writes to TQM/data/error_logs.csv
and TQM/data/audit_logs.csv, so the schema stays consistent no matter
which service or UI component triggers a log entry.

Design notes:
- CSV headers already exist from the documentation foundation batch;
  we append rows, we never overwrite the header.
- IDs are generated as an incrementing counter based on existing rows,
  so IDs stay stable across runs.
- Every write is wrapped defensively: logging must never itself crash
  the application.
"""
import csv
import os
import threading
from datetime import datetime

from app.config import ERROR_LOG_CSV, AUDIT_LOG_CSV, DEFECT_LOG_CSV
from app.utils import session

_lock = threading.Lock()

_ERROR_HEADER = ["timestamp", "error_id", "module", "error_type", "severity",
                  "user_id", "action", "status", "message_reference"]
_AUDIT_HEADER = ["timestamp", "user_id", "role", "module", "action",
                  "record_id", "result", "description"]
_DEFECT_HEADER = ["defect_id", "date", "module", "category", "title", "description",
                   "severity", "priority", "status", "root_cause", "corrective_action", "test_case"]


def _next_id(csv_path: str, id_column: str, prefix: str) -> str:
    """Compute the next sequential ID (e.g. ERR-0007) from an existing CSV."""
    count = 0
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for _ in reader:
                    count += 1
        except Exception:
            count = 0
    return f"{prefix}-{count + 1:04d}"


def _append_row(csv_path: str, header: list, row: dict) -> None:
    """Append a row to a CSV, creating the file with a header if missing."""
    with _lock:
        file_exists = os.path.exists(csv_path)
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        write_header = not file_exists or os.path.getsize(csv_path) == 0
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if write_header:
                writer.writeheader()
            writer.writerow(row)


def log_error(module: str, error_type: str, severity: str, action: str,
              status: str = "Open", message_reference: str = "") -> str:
    """
    Record an error/exception in TQM/data/error_logs.csv.
    Returns the generated error_id. Never raises.
    """
    try:
        error_id = _next_id(ERROR_LOG_CSV, "error_id", "ERR")
        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "error_id": error_id,
            "module": module,
            "error_type": error_type,
            "severity": severity,
            "user_id": session.get_user(),
            "action": action,
            "status": status,
            "message_reference": message_reference,
        }
        _append_row(ERROR_LOG_CSV, _ERROR_HEADER, row)
        return error_id
    except Exception:
        # Logging must never crash the application it is protecting.
        return "ERR-UNLOGGED"


def log_audit(module: str, action: str, record_id: str, result: str,
              description: str = "") -> str:
    """
    Record an important operation in TQM/data/audit_logs.csv.
    Returns nothing meaningful to check; never raises.
    """
    try:
        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_id": session.get_user(),
            "role": session.get_role(),
            "module": module,
            "action": action,
            "record_id": record_id,
            "result": result,
            "description": description,
        }
        _append_row(AUDIT_LOG_CSV, _AUDIT_HEADER, row)
        return "logged"
    except Exception:
        return "unlogged"


def log_defect(defect_id: str, date: str, module: str, category: str, title: str,
               description: str, severity: str, priority: str, status: str,
               root_cause: str = "", corrective_action: str = "", test_case: str = "") -> str:
    """
    Record a bug in TQM/data/defect_log.csv (Q09 feature #4: Bug Tracker).

    This is append-only, same as error/audit logs: every call writes a
    NEW row reflecting the bug's state at that moment, so the CSV holds
    a full history (creation, then each status change) rather than
    being overwritten in place. That history is exactly what later
    Pareto/Fishbone/PDCA analysis needs. Never raises — logging must not
    crash the application it is protecting.
    """
    try:
        row = {
            "defect_id": defect_id,
            "date": date,
            "module": module,
            "category": category,
            "title": title,
            "description": description,
            "severity": severity,
            "priority": priority,
            "status": status,
            "root_cause": root_cause,
            "corrective_action": corrective_action,
            "test_case": test_case,
        }
        _append_row(DEFECT_LOG_CSV, _DEFECT_HEADER, row)
        return "logged"
    except Exception:
        return "unlogged"
