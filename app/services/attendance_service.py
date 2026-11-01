"""Hostel roll call: staff mark Present/Absent; approved leave shows as Leave."""
from datetime import date, datetime

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
    session.require_roles(session.STAFF_ROLES, "mark attendance")
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
    session.require_roles(session.STAFF_ROLES, "view the attendance roster")
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
    day = day or date.today().isoformat()
    counts = {"Present": 0, "Absent": 0, "Leave": 0, "Unmarked": 0}
    for item in get_roster(day):
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
                               "AND to_date >= ? AND from_date <= ?", (student_id, start, date.today().isoformat())):
            lo = max(row["from_date"], start)
            hi = min(row["to_date"], date.today().isoformat())
            counts["Leave"] += (date.fromisoformat(hi) - date.fromisoformat(lo)).days + 1
        counts["days"] = int(days)
        return counts
    finally:
        conn.close()
