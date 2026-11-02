"""
Loads the class list as demo data: students, rooms, allocations, student
logins, and a few sample complaints and leaves.

    python -m app.database.seed_demo            # students, rooms, logins + sample complaints/leaves
    python -m app.database.seed_demo --real     # students, rooms, logins only

Safe to run more than once (existing students/rooms are skipped).
Everything goes through the normal services, so all validation applies,
but audit/error entries are written to a throwaway file so the real
TQM/data evidence logs stay free of demo activity.

Registration number = 24103020 + two-digit roll number (Mayank is roll 37).
Only Mayank's roll is known; the others are ASSIGNED in alphabetical order
and contact numbers are made up — replace both with real values.
"""
import os
from datetime import date, datetime, timedelta, timezone
import random
import tempfile
import sqlite3

import app.config as config
import app.utils.logging_service as logging_service
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import (auth_service, student_service, room_service, allocation_service,
                           complaint_service, leave_service)
from app.utils.validation import ValidationError, validate_registration_number, validate_contact_number

# (name, block) — block is only used to group students into rooms; edit freely.
STUDENTS = [
    ("Ajay Bora", "A"), ("Aman Yadav", "A"), ("Ankita", "B"), ("Anmol Joshi", "A"),
    ("Anushka Puri", "B"), ("Ashish Bora", "A"), ("Ashish Dumka", "A"), ("Bharat Pant", "A"),
    ("Chandan Latwal", "A"), ("Deepak Joshi", "A"), ("Farhan Al Ameen", "A"), ("Gaurav Adhikari", "A"),
    ("Gaurav Sharma", "A"), ("Harshit Bhatt", "A"), ("Harshit Bhoj", "A"), ("Harshit Joshi", "A"),
    ("Harshit Singh Thaguna", "A"), ("Jatin Mehta", "A"), ("Jay Paneru", "A"),
    ("Jitendra Mohan Purohit", "A"), ("Karan Das", "A"), ("Kartik Pandey", "A"),
    ("Khusbu Tewari", "B"), ("Khushi Kandpal", "B"), ("Km Komal", "B"), ("Komal Bohra", "B"),
    ("Lakshya Verma", "A"), ("Lokesh Maurya", "A"), ("Lokesh Pargain", "A"), ("Mayank Joshi", "A"),
    ("Mukesh Chandra", "A"), ("Natik Bhandari", "A"), ("Neeraj Nautiyal", "A"), ("Neha Rawat", "B"),
    ("Nikhil Vinay", "A"), ("Nitin Rawat", "A"), ("Parth Khatri", "A"), ("Piyush Bhatt", "A"),
    ("Prabhat Bhainsora", "A"), ("Rahul Mehra", "A"), ("Rohan Gupta", "A"), ("Rohit Sharma", "A"),
    ("Sachin Sharma", "A"), ("Sagar Joshi", "A"), ("Sanchit Pal", "A"), ("Sanjana Parsad", "B"),
    ("Shahnawaz", "A"), ("Shubh Chauhan", "A"), ("Sidhi Baluja", "B"), ("Suhani Kesarwani", "B"),
    ("Swati Melkani", "B"), ("Tanmay Pandey", "A"), ("Tanushree Negi", "B"), ("Ujjwal Adhikari", "A"),
    ("Vansh Khurana", "A"), ("Vanshika Malik", "B"),
]

KNOWN_ROLL = {"Mayank Joshi": 37}
REG_PREFIX = "24103020"
DEFAULT_PASSWORD = auth_service.SEED_PASSWORD
EXTRA_EMPTY_ROOMS = {"A": "A201", "B": "B201"}

SAMPLE_COMPLAINTS = [
    ("Nitin Rawat", "Food", "Dinner quality in the mess was poor today.", None, None),
    ("Jay Paneru", "Washroom", "Washroom tap in the corridor is leaking.", None, None),
    ("Karan Das", "Maintenance", "Ceiling fan in the room is not working.", "Hostel Maintenance", None),
    ("Sachin Sharma", "Washroom", "Washroom door lock is broken.", "Hostel Maintenance", "Lock replaced."),
    ("Khushi Kandpal", "Cleanliness", "Corridor is not cleaned regularly.", None, None),
]
def _day(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


SAMPLE_LEAVES = [
    ("Deepak Joshi", _day(2), _day(6), "Home visit", False),
    ("Lokesh Maurya", _day(-7), _day(-4), "Home visit", True),
    ("Neha Rawat", _day(4), _day(8), "Home visit", False),
]


def _roll(index: int, name: str) -> int:
    """Alphabetical position, shifted so Mayank lands on his real roll 37."""
    mayank_index = next(i for i, (n, _) in enumerate(STUDENTS, start=1) if n == "Mayank Joshi")
    if name in KNOWN_ROLL:
        return KNOWN_ROLL[name]
    return index if index < mayank_index else index + (KNOWN_ROLL["Mayank Joshi"] - mayank_index)


def _contact(index: int) -> str:
    rng = random.Random(index * 7919)
    return str(rng.choice([6, 7, 8, 9, 9, 9])) + "".join(str(rng.randint(0, 9)) for _ in range(9))


def _update_student(student_id: int, reg: str, contact: str) -> None:
    conn = db_module.get_connection()
    try:
        conn.execute("UPDATE students SET registration_number = ?, contact_number = ? WHERE student_id = ?",
                     (validate_registration_number(reg), validate_contact_number(contact), student_id))
        conn.commit()
    finally:
        conn.close()


def _username(name: str, taken: set) -> str:
    base = "_".join(name.lower().split())[:26]
    candidate, n = base, 2
    while candidate in taken:
        candidate = f"{base}{n}"
        n += 1
    taken.add(candidate)
    return candidate


def run_seed(db_path: str = None, include_samples: bool = True) -> dict:
    scratch = tempfile.mkdtemp()
    saved = (db_module.DATABASE_PATH, config.DATABASE_PATH,
             logging_service.ERROR_LOG_CSV, logging_service.AUDIT_LOG_CSV)
    if db_path:
        db_module.DATABASE_PATH = config.DATABASE_PATH = db_path
    logging_service.ERROR_LOG_CSV = os.path.join(scratch, "error_logs.csv")
    logging_service.AUDIT_LOG_CSV = os.path.join(scratch, "audit_logs.csv")
    summary = {"students": 0, "rooms": 0, "allocations": 0, "accounts": 0, "complaints": 0, "leaves": 0, "updated": 0}
    try:
        initialize_database()
        all_students = student_service.get_all_students()
        existing_students = {s["registration_number"]: s["student_id"] for s in all_students}
        by_name = {s["name"]: s for s in all_students}
        existing_rooms = {r["room_number"]: r["room_id"] for r in room_service.get_all_rooms()}
        taken_usernames = {u["username"] for u in auth_service.list_users()}
        ids = {}
        new_students = set()

        for i, (name, block) in enumerate(STUDENTS, start=1):
            reg = f"{REG_PREFIX}{_roll(i, name):02d}"
            contact = _contact(i)
            old = by_name.get(name)
            if old is not None and old["registration_number"].startswith("DEMO") and reg not in existing_students:
                _update_student(old["student_id"], reg, contact)
                summary["updated"] += 1
            if reg in existing_students:
                ids[name] = existing_students[reg]
                continue
            if old is not None:
                ids[name] = old["student_id"]
                continue
            ids[name] = student_service.add_student(name, reg, contact)
            new_students.add(name)
            summary["students"] += 1

        by_block = {"A": [], "B": []}
        for name, block in STUDENTS:
            by_block[block].append(name)

        for block, names in by_block.items():
            for index, name in enumerate(names):
                room_number = f"{block}{101 + index // 2}"
                if room_number not in existing_rooms:
                    existing_rooms[room_number] = room_service.add_room(room_number, "Double", 2)
                    summary["rooms"] += 1
                if name in new_students:
                    allocation_service.allocate_room(ids[name], existing_rooms[room_number])
                    summary["allocations"] += 1
        for room_number in EXTRA_EMPTY_ROOMS.values():
            if room_number not in existing_rooms:
                existing_rooms[room_number] = room_service.add_room(room_number, "Double", 2)
                summary["rooms"] += 1

        for name, _ in STUDENTS:
            if name not in new_students:
                continue
            username = _username(name, taken_usernames)
            auth_service.create_user(username, DEFAULT_PASSWORD, "Student", ids[name], must_change_password=True)
            summary["accounts"] += 1

        auth_service.flag_accounts_using_seed_password()

        for name, category, text, assignee, notes in (SAMPLE_COMPLAINTS if include_samples else []):
            if name not in new_students:
                continue
            cid = complaint_service.create_complaint(ids[name], category, text)
            if assignee:
                complaint_service.assign_complaint(cid, assignee)
            if notes:
                complaint_service.resolve_complaint(cid, notes)
            summary["complaints"] += 1

        for name, start, end, reason, returned in (SAMPLE_LEAVES if include_samples else []):
            if name not in new_students:
                continue
            lid = leave_service.record_leave(ids[name], start, end, reason)
            if returned:
                leave_service.mark_returned(lid)
            summary["leaves"] += 1
        return summary
    finally:
        (db_module.DATABASE_PATH, config.DATABASE_PATH,
         logging_service.ERROR_LOG_CSV, logging_service.AUDIT_LOG_CSV) = saved


def seed_test_accounts_and_data(db_path: str = None) -> dict:
    """
    Ensures testing accounts for each role with preloaded demo data:
      - Super Admin: superadmin / admin123 (and admin / admin123)
      - Administrator: hostel_admin / admin123
      - Staff: hostel_staff / staff123 (and warden / warden123)
      - Student: student / student123 (and mayankjoshi13 / student123); student_girl / student123 (girls block)
    All test accounts have must_change_password=0 and status='Active'.
    Also seeds attendance records, notices across audiences, leaves, complaints,
    events, fines, wardens and workers.
    """
    target_db = db_path or db_module.DATABASE_PATH
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    today_d = date.today()
    summary = {}

    try:
        # 1. Identify or create demo student
        cur.execute("SELECT student_id FROM students WHERE registration_number = '2410302037'")
        row = cur.fetchone()
        if row is None:
            cur.execute("SELECT student_id FROM students WHERE name LIKE '%Mayank%' ORDER BY student_id LIMIT 1")
            row = cur.fetchone()
        if row is None:
            cur.execute("SELECT student_id FROM students ORDER BY student_id LIMIT 1")
            row = cur.fetchone()

        if row is None:
            cur.execute("INSERT INTO students (name, registration_number, contact_number) "
                        "VALUES ('Mayank Joshi', '2410302037', '9876543210')")
            demo_student_id = cur.lastrowid
        else:
            demo_student_id = row["student_id"]

        # Ensure demo student has an active room allocation
        cur.execute("SELECT allocation_id, room_id FROM allocations WHERE student_id = ? AND status = 'Active'",
                    (demo_student_id,))
        demo_alloc = cur.fetchone()
        if demo_alloc is None:
            cur.execute("SELECT r.room_id FROM rooms r LEFT JOIN allocations a ON a.room_id = r.room_id AND a.status = 'Active' "
                        "GROUP BY r.room_id HAVING COUNT(a.allocation_id) < r.capacity LIMIT 1")
            room_row = cur.fetchone()
            if room_row is None:
                cur.execute("INSERT INTO rooms (room_number, room_type, capacity) VALUES ('A201', 'Double', 2)")
                demo_room_id = cur.lastrowid
            else:
                demo_room_id = room_row["room_id"]
            cur.execute("INSERT INTO allocations (student_id, room_id, status) VALUES (?, ?, 'Active')",
                        (demo_student_id, demo_room_id))
            conn.commit()

        for name, block in STUDENTS:
            cur.execute("UPDATE students SET gender = ? WHERE name = ? AND (gender IS NULL OR gender = '')",
                        ("Female" if block == "B" else "Male", name))
        cur.execute("UPDATE rooms SET hostel_type = CASE WHEN room_number LIKE 'B%' THEN 'Girls' ELSE 'Boys' END "
                    "WHERE hostel_type IS NULL OR hostel_type = ''")
        cur.execute("UPDATE rooms SET floor = CAST(substr(room_number, 2, 1) AS INTEGER) "
                    "WHERE floor = 0 AND substr(room_number, 2, 1) GLOB '[0-9]'")
        cur.execute("SELECT student_id FROM students WHERE name = 'Neha Rawat' LIMIT 1")
        girl_row = cur.fetchone()
        girl_student_id = girl_row["student_id"] if girl_row else None
        conn.commit()

        # 2. Dedicated test accounts with must_change_password=0
        test_accounts = [
            ("superadmin", "admin123", "Super Admin", None),
            ("admin", "admin123", "Super Admin", None),
            ("hostel_admin", "admin123", "Administrator", None),
            ("hostel_staff", "staff123", "Staff", None),
            ("warden", "warden123", "Warden", None),
            ("student", "student123", "Student", demo_student_id),
            ("student_girl", "student123", "Student", girl_student_id),
            ("mayankjoshi13", "student123", "Student", demo_student_id),
        ]
        accounts_count = 0
        for username, pwd, role, sid in test_accounts:
            if role == "Student" and sid is None:
                continue
            cur.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            existing_user = cur.fetchone()
            h = auth_service._hash_password(pwd)
            if existing_user is None:
                cur.execute(
                    "INSERT INTO users (username, password_hash, role, student_id, must_change_password, status, failed_attempts, locked_until) "
                    "VALUES (?, ?, ?, ?, 0, 'Active', 0, NULL)",
                    (username, h, role, sid)
                )
                accounts_count += 1
            else:
                cur.execute(
                    "UPDATE users SET password_hash = ?, role = ?, student_id = COALESCE(?, student_id), "
                    "must_change_password = 0, status = 'Active', failed_attempts = 0, locked_until = NULL "
                    "WHERE user_id = ?",
                    (h, role, sid, existing_user["user_id"])
                )
        conn.commit()
        summary["accounts_verified"] = len(test_accounts)

        # 3. Wardens
        sample_wardens = [
            ("Dr. Arvind Bhatt", "Male", "9876543210", "Boys Hostel Block A", "5:00 PM - 7:00 PM", "warden"),
            ("Dr. Sunita Sharma", "Female", "9876543211", "Girls Hostel Block B", "4:30 PM - 6:30 PM", "sunita_warden"),
        ]
        for name, gender, contact, hostel, hours, u in sample_wardens:
            cur.execute("SELECT warden_id FROM wardens WHERE contact_number = ? OR username = ?", (contact, u))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO wardens (name, gender, contact_number, hostel_name, office_hours, username, status) "
                            "VALUES (?, ?, ?, ?, ?, ?, 'Active')", (name, gender, contact, hostel, hours, u))
        conn.commit()

        # 4. Workers & Worker Attendance
        sample_workers = [
            ("Ramesh Kumar", "Electrician", "9876540001"),
            ("Suresh Verma", "Plumber", "9876540002"),
            ("Rajesh Singh", "Cleaner", "9876540003"),
            ("Mahesh Chand", "Carpenter", "9876540004"),
            ("Dinesh Rawat", "Security Guard", "9876540005"),
        ]
        worker_ids = []
        for name, trade, contact in sample_workers:
            cur.execute("SELECT worker_id FROM workers WHERE contact_number = ?", (contact,))
            w_row = cur.fetchone()
            if w_row is None:
                cur.execute("INSERT INTO workers (name, trade, contact_number, status) VALUES (?, ?, ?, 'Active')",
                            (name, trade, contact))
                worker_ids.append(cur.lastrowid)
            else:
                worker_ids.append(w_row["worker_id"])
        conn.commit()

        for offset in (0, -1, -2):
            w_day = (today_d + timedelta(days=offset)).isoformat()
            for wid in worker_ids:
                cur.execute("INSERT OR IGNORE INTO worker_attendance (worker_id, work_date, status) VALUES (?, ?, 'Present')",
                            (wid, w_day))
        conn.commit()

        # 5. Student Attendance for today and recent days
        cur.execute("SELECT student_id FROM allocations WHERE status = 'Active'")
        active_sids = [r["student_id"] for r in cur.fetchall()]
        if demo_student_id not in active_sids:
            active_sids.append(demo_student_id)

        att_count = 0
        for offset in range(0, -14, -1):
            att_day = (today_d + timedelta(days=offset)).isoformat()
            for idx, sid in enumerate(active_sids):
                st = "Present"
                if sid != demo_student_id and (sid + abs(offset)) % 7 == 0:
                    st = "Absent"
                cur.execute(
                    "INSERT INTO student_attendance (student_id, att_date, status, marked_by) VALUES (?, ?, ?, 'hostel_admin') "
                    "ON CONFLICT(student_id, att_date) DO NOTHING",
                    (sid, att_day, st)
                )
                att_count += 1
        conn.commit()
        summary["attendance_records"] = att_count

        # 6. Notices across all audiences
        sample_notices = [
            ("Annual Hostel Day & Cultural Fest 2026",
             "Registrations are now open for the Annual Hostel Cultural and Sports Fest 2026. Events include Badminton, Table Tennis, Chess, Coding Hackathon, and Musical Night. Contact the sports committee representatives or sign up at the hostel office before the 15th.",
             "All", None, "hostel_admin"),
            ("Mess Menu Revision Committee Meeting this Friday",
             "A meeting of the Mess Committee with student representatives and the chief warden is scheduled for this Friday at 5:00 PM in the Common Hall. Topics will include seasonal vegetables, Sunday breakfast options, and dietary feedback.",
             "All", None, "warden"),
            ("Maintenance Notice: Water Supply Schedule for Block A",
             "Scheduled overhead tank cleaning in Block A will take place tomorrow between 10:00 AM and 2:00 PM. Water supply will be temporarily paused during this window. Residents are advised to store sufficient water beforehand.",
             "Boys", None, "hostel_admin"),
            ("Gym and Sports Equipment Maintenance for Block B",
             "The gym facilities and indoor games equipment in Block B recreation room have been upgraded with new treadmills, dumbbells, and yoga mats. Please ensure proper gym etiquette and return equipment to designated racks.",
             "Girls", None, "warden"),
            ("Wi-Fi Maintenance & High-Speed Bandwidth Upgrade Scheduled",
             "IT services will be upgrading access points across both hostel blocks on Saturday from 2:00 AM to 5:00 AM. Internet access may experience brief intermittent drops during this maintenance window.",
             "All", None, "superadmin"),
            ("Room Inventory Verification Reminder",
             "Your room inventory verification for Semester II is pending. Please meet your block warden during office hours to complete the sign-off.",
             "Student", demo_student_id, "warden"),
        ]
        for title, body, audience, sid, author in sample_notices:
            cur.execute("SELECT notice_id FROM notices WHERE title = ?", (title,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO notices (title, body, audience, student_id, created_by) VALUES (?, ?, ?, ?, ?)",
                            (title, body, audience, sid, author))
        conn.commit()

        # 7. Leaves
        cur.execute("SELECT COUNT(*) AS n FROM leaves")
        if cur.fetchone()["n"] < 3:
            cur.execute("SELECT room_id FROM allocations WHERE student_id = ? AND status = 'Active'", (demo_student_id,))
            demo_alloc_row = cur.fetchone()
            demo_rid = demo_alloc_row["room_id"] if demo_alloc_row else 1
            past_start = (today_d - timedelta(days=12)).isoformat()
            past_end = (today_d - timedelta(days=7)).isoformat()
            cur.execute(
                "INSERT INTO leaves (student_id, room_id, from_date, to_date, reason, status, returned_at) "
                "VALUES (?, ?, ?, ?, 'Attended University Technical Fest & Hackathon', 'Returned', ?)",
                (demo_student_id, demo_rid, past_start, past_end, past_end)
            )
            cur.execute("SELECT student_id, room_id FROM allocations WHERE status = 'Active' AND student_id != ? LIMIT 2",
                        (demo_student_id,))
            other_allocs = cur.fetchall()
            if len(other_allocs) > 0:
                s1, r1 = other_allocs[0]["student_id"], other_allocs[0]["room_id"]
                cur.execute(
                    "INSERT INTO leaves (student_id, room_id, from_date, to_date, reason, status) "
                    "VALUES (?, ?, ?, ?, 'Home visit for family function', 'On Leave')",
                    (s1, r1, (today_d - timedelta(days=1)).isoformat(), (today_d + timedelta(days=4)).isoformat())
                )
            if len(other_allocs) > 1:
                s2, r2 = other_allocs[1]["student_id"], other_allocs[1]["room_id"]
                cur.execute(
                    "INSERT INTO leaves (student_id, room_id, from_date, to_date, reason, status) "
                    "VALUES (?, ?, ?, ?, 'Medical consultation & rest', 'On Leave')",
                    (s2, r2, (today_d + timedelta(days=2)).isoformat(), (today_d + timedelta(days=6)).isoformat())
                )
            conn.commit()

        # 7b. A pending leave to approve and a few visitors
        if cur.execute("SELECT 1 FROM leaves WHERE status = 'Pending'").fetchone() is None:
            free = cur.execute(
                "SELECT al.student_id, al.room_id FROM allocations al JOIN students s ON s.student_id = al.student_id "
                "WHERE al.status = 'Active' AND al.student_id != ? AND NOT EXISTS (SELECT 1 FROM leaves l "
                "WHERE l.student_id = al.student_id AND l.status IN ('On Leave', 'Pending')) "
                "ORDER BY (s.gender = 'Female') DESC, al.student_id LIMIT 1", (demo_student_id,)).fetchone()
            if free:
                cur.execute(
                    "INSERT INTO leaves (student_id, room_id, from_date, to_date, reason, status) "
                    "VALUES (?, ?, ?, ?, 'Sister''s wedding', 'Pending')",
                    (free["student_id"], free["room_id"], (today_d + timedelta(days=3)).isoformat(),
                     (today_d + timedelta(days=7)).isoformat()))
        if cur.execute("SELECT COUNT(*) AS n FROM visitors").fetchone()["n"] == 0:
            def _utc(days_back, hour, minute=0):
                local = (datetime.now() - timedelta(days=days_back)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                return local.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for sid, vname, rel, purpose, day, hour, stay in (
                    (demo_student_id, "Ramesh Joshi", "Parent", "Bringing supplies", 1, 17, None),
                    (demo_student_id, "Kunal Verma", "Friend", "Project discussion", 2, 11, 1),
                    (girl_student_id or demo_student_id, "Sunita Rawat", "Parent", "Routine visit", 1, 10, 2),
                    (demo_student_id, "Anil Mehra", "Relative", "Festival gift", 3, 20, 1)):
                cur.execute("INSERT INTO visitors (student_id, visitor_name, relation, purpose, in_time, out_time, logged_by) "
                            "VALUES (?, ?, ?, ?, ?, ?, 'hostel_staff')",
                            (sid, vname, rel, purpose, _utc(day, hour),
                             _utc(day, hour + stay) if stay else None))
        conn.commit()

        # 8. Complaints
        cur.execute("SELECT COUNT(*) AS n FROM complaints")
        if cur.fetchone()["n"] < 4:
            cur.execute(
                "INSERT INTO complaints (student_id, category, description, status, assigned_to) "
                "VALUES (?, 'Maintenance', 'Study lamp socket switch in room is loose and sparking intermittently.', 'Assigned', 'Electrician')",
                (demo_student_id,)
            )
            cur.execute(
                "INSERT INTO complaints (student_id, category, description, status) "
                "VALUES (?, 'Food', 'Dinner quality in the mess was sub-standard today.', 'Open')",
                (demo_student_id,)
            )
            cur.execute(
                "INSERT INTO complaints (student_id, category, description, status, assigned_to, resolved_at, resolution_notes) "
                "VALUES (?, 'Washroom', 'Corridor washroom tap leaking continuously.', 'Resolved', 'Plumber', datetime('now', '-1 day'), 'Replaced the rubber washer and valve.')",
                (demo_student_id,)
            )
            cur.execute(
                "INSERT INTO complaints (student_id, category, description, status) "
                "VALUES (?, 'Cleanliness', 'Common area water cooler surroundings need daily cleaning.', 'Open')",
                (demo_student_id,)
            )
            conn.commit()

        # 9. Events
        cur.execute("SELECT COUNT(*) AS n FROM events")
        if cur.fetchone()["n"] < 5:
            sample_events = [
                (today_d.isoformat(), "Hostel Roll Call & Floor Inspection", "Hostel Event"),
                ((today_d + timedelta(days=1)).isoformat(), "Mess Committee Review Meeting", "Hostel Event"),
                ((today_d + timedelta(days=4)).isoformat(), "Inter-Hostel Table Tennis Tournament", "Hostel Event"),
                ((today_d + timedelta(days=10)).isoformat(), "Career Guidance & Alumni Interaction Workshop", "Hostel Event"),
                ((today_d + timedelta(days=18)).isoformat(), "Hostel Cultural Night & Music Jam", "Hostel Event"),
                ((today_d + timedelta(days=25)).isoformat(), "Blood Donation Camp & Health Checkup", "Hostel Event"),
            ]
            for edate, etitle, ekind in sample_events:
                cur.execute("INSERT OR IGNORE INTO events (event_date, title, kind) VALUES (?, ?, ?)",
                            (edate, etitle, ekind))
            conn.commit()

        # 10. Fines
        cur.execute("SELECT COUNT(*) AS n FROM fines WHERE student_id = ?", (demo_student_id,))
        if cur.fetchone()["n"] == 0:
            cur.execute(
                "INSERT INTO fines (student_id, amount_paise, reason, status) "
                "VALUES (?, 20000, 'Late entry after hostel curfew hours without approved gate pass', 'Unpaid')",
                (demo_student_id,)
            )
            cur.execute(
                "INSERT INTO fines (student_id, amount_paise, reason, status, paid_at, payment_method, receipt_number) "
                "VALUES (?, 10000, 'Replacement fee for duplicate hostel identity card', 'Paid', datetime('now', '-2 days'), 'Cash', 'RCP-2026-001')",
                (demo_student_id,)
            )
            conn.commit()

        # 11. University Emergency Contacts & Gmail
        from app.services.emergency_service import seed_university_defaults
        seed_university_defaults()

        return summary
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        import sys
        result = run_seed(include_samples="--real" not in sys.argv)
        extra = seed_test_accounts_and_data()
    except ValidationError as exc:
        raise SystemExit(f"Seeding stopped: {exc}")
    print("Added:", ", ".join(f"{v} {k}" for k, v in result.items()))
    print("Test Accounts & Data:", extra)

