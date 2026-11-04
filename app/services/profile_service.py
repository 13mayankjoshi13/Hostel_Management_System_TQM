"""Everything the hostel knows about one student, for the profile opened from search."""
from app.database.db import get_connection
from app.services import attendance_service
from app.utils import session
from app.utils.timefmt import localise_rows
from app.utils.validation import ValidationError, validate_record_id


def student_profile(student_id: int) -> dict:
    session.require_roles(session.WARDEN_ROLES, "open student profiles")
    student_id = validate_record_id(student_id, "Select a student first.")
    conn = get_connection()
    try:
        student = conn.execute("SELECT student_id, name, registration_number, contact_number, gender, created_at "
                               "FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if student is None:
            raise ValidationError(f"No student found with ID {student_id}.")
        room = conn.execute(
            "SELECT r.room_number, r.room_type, r.floor, r.hostel_type, al.allocated_at FROM allocations al "
            "JOIN rooms r ON r.room_id = al.room_id WHERE al.student_id = ? AND al.status = 'Active'",
            (student_id,)).fetchone()
        account = conn.execute("SELECT username, status FROM users WHERE student_id = ? ORDER BY user_id LIMIT 1",
                               (student_id,)).fetchone()
        leaves = [dict(r) for r in conn.execute(
            "SELECT from_date, to_date, reason, status FROM leaves WHERE student_id = ? ORDER BY leave_id DESC LIMIT 5",
            (student_id,))]
        complaints = [dict(r) for r in conn.execute(
            "SELECT category, description, status FROM complaints WHERE student_id = ? ORDER BY complaint_id DESC LIMIT 5",
            (student_id,))]
        fines = [dict(r) for r in conn.execute(
            "SELECT amount_paise, reason, status FROM fines WHERE student_id = ? ORDER BY fine_id DESC LIMIT 5",
            (student_id,))]
        unpaid = conn.execute("SELECT COALESCE(SUM(amount_paise), 0) FROM fines WHERE student_id = ? AND status = 'Unpaid'",
                              (student_id,)).fetchone()[0]
        visitors = localise_rows([dict(r) for r in conn.execute(
            "SELECT visitor_name, relation, purpose, in_time FROM visitors WHERE student_id = ? "
            "ORDER BY visitor_id DESC LIMIT 5", (student_id,))], "in_time")
        warden = None
        if room and room["hostel_type"]:
            warden = conn.execute("SELECT name, contact_number FROM wardens WHERE status = 'Active' AND gender = ? "
                                  "ORDER BY warden_id LIMIT 1",
                                  ("Female" if room["hostel_type"] == "Girls" else "Male",)).fetchone()
        profile = {
            "student": dict(student), "room": dict(room) if room else None,
            "account": dict(account) if account else None,
            "warden": dict(warden) if warden else None,
            "leaves": leaves, "complaints": complaints, "fines": fines, "unpaid_paise": unpaid, "visitors": visitors,
        }
    finally:
        conn.close()
    profile["attendance"] = attendance_service.student_summary(student_id, 30)
    return profile
