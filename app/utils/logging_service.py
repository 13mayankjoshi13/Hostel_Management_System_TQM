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
import json
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
                   "severity", "priority", "status", "root_cause", "corrective_action", "test_case",
                   "reported_by", "fixed_by"]


def _next_id(csv_path: str, id_column: str, prefix: str) -> str:
    """
    Next sequential ID (e.g. ERR-0007): one more than the highest number already used, counting rows
    waiting in the .pending queue. The file is read leniently, so a log re-saved by Excel in another
    encoding, or with rows deleted by hand, can never make an old ID repeat.
    """
    highest = 0
    numbers = []
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", newline="", encoding="utf-8", errors="replace") as f:
                numbers += [row.get(id_column) or "" for row in csv.DictReader(f)]
        except (OSError, csv.Error):
            pass
    try:
        numbers += [row.get(id_column) or "" for row in _read_pending(csv_path)]
    except (OSError, ValueError):
        pass
    for value in numbers:
        head, _, tail = str(value).rpartition("-")
        if head == prefix and tail.isdigit():
            highest = max(highest, int(tail))
    return f"{prefix}-{highest + 1:04d}"


_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _neutralise(value):
    """Stop spreadsheet apps from running user text as a formula when a log is opened."""
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def _upgrade_header(csv_path: str, header: list) -> None:
    """If an older log has fewer columns, rewrite it with the current header (old rows get blanks) so new rows are not lost."""
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        existing = reader.fieldnames
        if existing is None or list(existing) == header:
            return
        rows = list(reader)
    temp = csv_path + ".tmp"
    with open(temp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore", restval="")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, csv_path)


def _repair_encoding(csv_path: str) -> None:
    """A log re-saved by Excel in Windows encoding is not valid UTF-8; rewrite it so appends keep working."""
    with open(csv_path, "rb") as f:
        raw = f.read()
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            f.write(text)


def _write_rows(csv_path: str, header: list, rows: list) -> None:
    file_exists = os.path.exists(csv_path)
    if file_exists and os.path.getsize(csv_path) > 0:
        _repair_encoding(csv_path)
        _upgrade_header(csv_path, header)
    write_header = not file_exists or os.path.getsize(csv_path) == 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({key: _neutralise(val) for key, val in row.items()})


def _pending_path(csv_path: str) -> str:
    return csv_path + ".pending"


def _read_pending(csv_path: str) -> list:
    path = _pending_path(csv_path)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _append_row(csv_path: str, header: list, row: dict) -> None:
    """
    Append a row to a CSV, creating the file with a header if missing. If the CSV cannot be written
    (on Windows, while it is open in Excel), the row is queued in '<name>.pending' and added the next
    time the CSV is writable, so evidence is delayed rather than lost.
    """
    with _lock:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        try:
            queued = _read_pending(csv_path)
            _write_rows(csv_path, header, queued + [row])
            if queued:
                os.remove(_pending_path(csv_path))
        except OSError:
            with open(_pending_path(csv_path), "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")


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
               root_cause: str = "", corrective_action: str = "", test_case: str = "",
               reported_by: str = "", fixed_by: str = "") -> str:
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
            "reported_by": reported_by or "",
            "fixed_by": fixed_by or "",
        }
        _append_row(DEFECT_LOG_CSV, _DEFECT_HEADER, row)
        return "logged"
    except Exception as exc:
        log_error("Bug", type(exc).__name__, "High", "log_defect", status="Open",
                   message_reference=f"Defect {defect_id} could not be written to the defect log: {exc}")
        return "unlogged"
