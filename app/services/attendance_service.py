"""Hostel roll call: admins mark Present/Absent; approved leave shows as Leave."""
import csv
from datetime import date, datetime, timedelta

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit
from app.utils.validation import ATTENDANCE_STATUSES, ValidationError, validate_record_id


def _clean_date(value) -> str:
    try:
        parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Enter the date as YYYY-MM-DD.")
    if parsed > date.today():
        raise ValidationError("Attendance cannot be marked for a future date.")
    return parsed.isoformat()


def _on_leave(cur, student_id: int, day: str) -> bool:
    cur.execute("SELECT 1 FROM leaves WHERE student_id = ? AND status = 'On Leave' "
                "AND from_date <= ? AND to_date >= ?", (student_id, day, day))
    return cur.fetchone() is not None


def mark_attendance(student_id: int, day: str, status: str) -> None:
    session.require_roles(session.ADMIN_ROLES, "mark attendance")
    student_id = validate_record_id(student_id, "Select a student first.")
    day = _clean_date(day)
    if status not in ATTENDANCE_STATUSES:
        raise ValidationError("Attendance must be Present or Absent.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        if cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone() is None:
            raise ValidationError(f"No student found with ID {student_id}.")
        if _on_leave(cur, student_id, day):
            raise ValidationError("This student is on approved leave that day; attendance shows as Leave.")
        cur.execute("INSERT INTO student_attendance (student_id, att_date, status, marked_by) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(student_id, att_date) DO UPDATE SET status = excluded.status, "
                    "marked_by = excluded.marked_by", (student_id, day, status, session.get_user()))
        conn.commit()
        log_audit("Attendance", "Mark", str(student_id), "Success", f"{status} on {day}.")
    finally:
        conn.close()


def get_roster(day: str) -> list:
    """Every student with an active room and their status for the day."""
    session.require_roles(session.ADMIN_ROLES, "view the attendance roster")
    return _roster(day)


def _roster(day: str) -> list:
    day = _clean_date(day)
    conn = get_connection()
    try:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT s.student_id, s.name, s.registration_number, r.room_number, a.status AS marked "
            "FROM allocations al JOIN students s ON s.student_id = al.student_id "
            "JOIN rooms r ON r.room_id = al.room_id "
            "LEFT JOIN student_attendance a ON a.student_id = s.student_id AND a.att_date = ? "
            "WHERE al.status = 'Active' ORDER BY r.room_number, s.name", (day,)).fetchall()
        roster = []
        for row in rows:
            item = dict(row)
            item["status"] = "Leave" if _on_leave(cur, item["student_id"], day) else (item.pop("marked") or "Unmarked")
            item.pop("marked", None)
            roster.append(item)
        return roster
    finally:
        conn.close()


def attendance_counts(day: str = None) -> dict:
    """Present / Absent / Leave / Unmarked totals across allocated students for the day."""
    session.require_roles(session.STAFF_ROLES, "view attendance totals")
    day = day or date.today().isoformat()
    counts = {"Present": 0, "Absent": 0, "Leave": 0, "Unmarked": 0}
    for item in _roster(day):
        counts[item["status"]] += 1
    return counts


def student_summary(student_id=None, days: int = 30) -> dict:
    """A student's own Present/Absent/Leave days over the last `days` days."""
    if student_id is None:
        student_id = session.get_student_id()
    session.require_own_or_staff(student_id, "view this attendance")
    start = date.fromordinal(date.today().toordinal() - int(days) + 1).isoformat()
    conn = get_connection()
    try:
        cur = conn.cursor()
        counts = {"Present": 0, "Absent": 0, "Leave": 0}
        for status, total in cur.execute(
                "SELECT status, COUNT(*) FROM student_attendance WHERE student_id = ? AND att_date >= ? "
                "GROUP BY status", (student_id, start)):
            counts[status] = total
        for row in cur.execute("SELECT from_date, to_date FROM leaves WHERE student_id = ? "
                               "AND status IN ('On Leave', 'Returned') AND to_date >= ? AND from_date <= ?", (student_id, start, date.today().isoformat())):
            lo = max(row["from_date"], start)
            hi = min(row["to_date"], date.today().isoformat())
            counts["Leave"] += (date.fromisoformat(hi) - date.fromisoformat(lo)).days + 1
        counts["days"] = int(days)
        return counts
    finally:
        conn.close()


LOW_ATTENDANCE_PERCENT = 75.0


def _month_bounds(month: str):
    try:
        first = datetime.strptime(str(month).strip(), "%Y-%m").date()
    except ValueError:
        raise ValidationError("Enter the month as YYYY-MM.")
    if first > date.today():
        raise ValidationError("That month has not started yet.")
    nxt = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    return first, min(nxt - timedelta(days=1), date.today())


def monthly_report(month: str) -> list:
    """Per-student Present / Absent / Leave days and attendance % (Present of Present + Absent) for a month."""
    session.require_roles(session.ADMIN_ROLES, "view attendance reports")
    first, last = _month_bounds(month)
    lo, hi = first.isoformat(), last.isoformat()
    conn = get_connection()
    try:
        students = conn.execute(
            "SELECT s.student_id, s.name, s.registration_number, r.room_number FROM allocations al "
            "JOIN students s ON s.student_id = al.student_id JOIN rooms r ON r.room_id = al.room_id "
            "WHERE al.status = 'Active' ORDER BY s.name").fetchall()
        report = []
        for st in students:
            marks = {d: status for d, status in conn.execute(
                "SELECT att_date, status FROM student_attendance WHERE student_id = ? AND att_date BETWEEN ? AND ?",
                (st["student_id"], lo, hi))}
            leave_days = set()
            for row in conn.execute("SELECT from_date, to_date FROM leaves WHERE student_id = ? "
                                    "AND status IN ('On Leave', 'Returned') AND to_date >= ? AND from_date <= ?",
                                    (st["student_id"], lo, hi)):
                day = max(date.fromisoformat(row["from_date"]), first)
                end = min(date.fromisoformat(row["to_date"]), last)
                while day <= end:
                    leave_days.add(day.isoformat())
                    day += timedelta(days=1)
            present = sum(1 for v in marks.values() if v == "Present")
            absent = sum(1 for v in marks.values() if v == "Absent")
            leave = len([d for d in leave_days if d not in marks])
            percent = round(present / (present + absent) * 100, 1) if present + absent else None
            report.append({"student_id": st["student_id"], "name": st["name"],
                           "registration_number": st["registration_number"], "room_number": st["room_number"],
                           "present": present, "absent": absent, "leave": leave, "percent": percent,
                           "low": percent is not None and percent < LOW_ATTENDANCE_PERCENT})
        return report
    finally:
        conn.close()


def export_report_csv(month: str, path: str) -> int:
    rows = monthly_report(month)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Student", "Registration No.", "Room", "Present", "Absent", "Leave", "Attendance %"])
        for r in rows:
            writer.writerow([r["name"], r["registration_number"], r["room_number"], r["present"], r["absent"],
                             r["leave"], "" if r["percent"] is None else r["percent"]])
    log_audit("Attendance", "Export", month, "Success", f"Monthly report exported ({len(rows)} students).")
    return len(rows)
