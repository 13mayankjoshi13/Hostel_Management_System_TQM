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
from datetime import date, timedelta
import random
import tempfile

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
DEFAULT_PASSWORD = "Welcome123"
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
            auth_service.create_user(username, DEFAULT_PASSWORD, "Student", ids[name])
            summary["accounts"] += 1

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


if __name__ == "__main__":
    try:
        import sys
        result = run_seed(include_samples="--real" not in sys.argv)
    except ValidationError as exc:
        raise SystemExit(f"Seeding stopped: {exc}")
    print("Added:", ", ".join(f"{v} {k}" for k, v in result.items()))
