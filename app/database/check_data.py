"""Health check for records already saved: finds data that today's rules would reject. Read-only. CLI: python -m app.database.check_data"""
import sqlite3

from app.database import db as db_module
from app.utils.logging_service import log_error
from app.utils.validation import (ValidationError, validate_contact_number, validate_registration_number,
                                  validate_student_name)

_CHECKS = (
    ("Duplicate registration numbers (ignoring case)",
     "SELECT UPPER(registration_number) AS item, COUNT(*) AS n FROM students "
     "GROUP BY UPPER(registration_number) HAVING n > 1"),
    ("Rooms holding more students than their capacity",
     "SELECT r.room_number AS item, COUNT(*) AS n FROM allocations a JOIN rooms r ON r.room_id = a.room_id "
     "WHERE a.status = 'Active' GROUP BY r.room_id HAVING n > r.capacity"),
    ("Students with more than one active room",
     "SELECT s.name AS item, COUNT(*) AS n FROM allocations a JOIN students s ON s.student_id = a.student_id "
     "WHERE a.status = 'Active' GROUP BY a.student_id HAVING n > 1"),
    ("Allocations pointing at a missing student or room",
     "SELECT 'allocation ' || allocation_id AS item, 1 AS n FROM allocations WHERE student_id NOT IN "
     "(SELECT student_id FROM students) OR room_id NOT IN (SELECT room_id FROM rooms)"),
    ("Complaints pointing at a missing student",
     "SELECT 'complaint ' || complaint_id AS item, 1 AS n FROM complaints WHERE student_id NOT IN "
     "(SELECT student_id FROM students)"),
    ("Open leaves for students with no active room",
     "SELECT s.name AS item, 1 AS n FROM leaves l JOIN students s ON s.student_id = l.student_id "
     "WHERE l.status = 'On Leave' AND l.student_id NOT IN "
     "(SELECT student_id FROM allocations WHERE status = 'Active')"),
    ("Student accounts not linked to a student record",
     "SELECT username AS item, 1 AS n FROM users WHERE role = 'Student' AND (student_id IS NULL OR student_id NOT IN "
     "(SELECT student_id FROM students))"),
)


def run_checks(db_path: str = None) -> list:
    """Returns [(problem, detail), ...]; empty when the data is clean."""
    conn = sqlite3.connect(db_path or db_module.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    issues = []
    try:
        for title, sql in _CHECKS:
            for row in conn.execute(sql).fetchall():
                issues.append((title, str(row["item"])))
        for row in conn.execute("SELECT name, registration_number, contact_number FROM students"):
            for label, check, value in (("name", validate_student_name, row["name"]),
                                        ("registration number", validate_registration_number, row["registration_number"]),
                                        ("contact number", validate_contact_number, row["contact_number"])):
                try:
                    check(value)
                except ValidationError:
                    issues.append((f"Student {label} that today's rules reject", f"{row['name']}: {value!r}"))
    finally:
        conn.close()
    return issues


def log_issues(issues: list) -> None:
    for title, detail in issues:
        log_error("Database", "DataQuality", "Medium", "check_data", status="Open",
                   message_reference=f"{title}: {detail}")


if __name__ == "__main__":
    found = run_checks()
    for title, detail in found:
        print(f"- {title}: {detail}")
    print(f"{len(found)} problem(s) found." if found else "No problems found.")
