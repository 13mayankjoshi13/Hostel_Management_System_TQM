"""Global search across students, rooms and complaints (staff roles only)."""
from app.database.db import get_connection
from app.utils import session

LIMIT = 6


def search(query: str) -> list:
    """Return [{kind, title, detail, screen[, student_id]}] for the text typed in the top bar."""
    session.require_roles(session.STAFF_ROLES, "search records")
    text = (query or "").strip()
    if len(text) < 2:
        return []
    like = f"%{text.replace('%', '').replace('_', '')}%"
    role = session.get_role()
    results = []
    conn = get_connection()
    try:
        if role in session.WARDEN_ROLES:
            for r in conn.execute(
                    "SELECT s.student_id, s.name, s.registration_number, s.contact_number, r.room_number "
                    "FROM students s LEFT JOIN allocations al ON al.student_id = s.student_id AND al.status = 'Active' "
                    "LEFT JOIN rooms r ON r.room_id = al.room_id "
                    "WHERE s.name LIKE ? OR s.registration_number LIKE ? OR s.contact_number LIKE ? "
                    "ORDER BY s.name LIMIT ?", (like, like, like, LIMIT)):
                room = f"Room {r['room_number']}" if r["room_number"] else "No room"
                results.append({"kind": "Student", "title": r["name"],
                                "detail": f"{r['registration_number']} · {room}", "screen": "Students",
                                "student_id": r["student_id"]})
        if role in session.ADMIN_ROLES:
            for r in conn.execute("SELECT room_number, room_type, capacity FROM rooms WHERE room_number LIKE ? "
                                  "ORDER BY room_number LIMIT ?", (like, LIMIT)):
                results.append({"kind": "Room", "title": f"Room {r['room_number']}",
                                "detail": f"{r['room_type']} · capacity {r['capacity']}", "screen": "Rooms"})
        for r in conn.execute(
                "SELECT c.complaint_id, c.category, c.status, s.name FROM complaints c "
                "JOIN students s ON s.student_id = c.student_id "
                "WHERE c.description LIKE ? OR c.category LIKE ? OR s.name LIKE ? OR CAST(c.complaint_id AS TEXT) = ? "
                "ORDER BY c.complaint_id DESC LIMIT ?", (like, like, like, text, LIMIT)):
            results.append({"kind": "Complaint", "title": f"#{r['complaint_id']} {r['category']}",
                            "detail": f"{r['name']} · {r['status']}", "screen": "Complaints"})
        return results
    finally:
        conn.close()
