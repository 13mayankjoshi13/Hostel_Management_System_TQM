"""
Feeds the bugs found during testing into the Bug Tracker (database plus
TQM/data/defect_log.csv) and walks each one through the same workflow the
Bug screen uses. Safe to re-run: a bug whose title is already logged is skipped.

    python -m app.database.log_bugs

Bugs stop at 'Fixed'; close them in the Bug screen after re-testing.
"""
from app.database.db import initialize_database
from app.services import bug_service

BUGS = [
    {
        "module": "Room", "category": "Validation", "severity": "Medium", "priority": "Medium",
        "title": "Room type and capacity are not checked against each other",
        "description": "Room screen accepts a Single room with capacity 5 or a Double room with capacity 1.",
        "root_cause": "add_room validated type and capacity separately; no rule linked them.",
        "corrective_action": "Added validate_type_capacity (Single 1, Double 2, Triple 3, Dormitory 4-10) and call it in add_room.",
        "test_case": "tests/test_bug_fixes.py::test_bug_001_*",
    },
    {
        "module": "Student", "category": "Validation", "severity": "Medium", "priority": "Medium",
        "title": "Contact number accepts numbers that cannot be Indian mobiles",
        "description": "Student screen accepts 10-digit contacts starting with 0-5 (e.g. 0123456789) and non-ASCII digits.",
        "root_cause": "validate_contact_number checked only digits-only and length 10; str.isdigit also allows non-ASCII digits.",
        "corrective_action": "Require ASCII digits and a first digit of 6, 7, 8 or 9 in validate_contact_number.",
        "test_case": "tests/test_bug_fixes.py::test_bug_002_*",
    },
    {
        "module": "Room", "category": "Data Integrity", "severity": "Medium", "priority": "Medium",
        "title": "Room numbers differing only in letter case are stored as separate rooms",
        "description": "Adding room 'Q1' and then 'q1' creates two rooms, so one physical room can exist twice.",
        "root_cause": "Duplicate check compared room_number exactly, and the value was stored as typed.",
        "corrective_action": "Store room numbers in upper case and compare with UPPER(room_number) in add_room.",
        "test_case": "tests/test_bug_fixes.py::test_bug_003_*",
    },
]


def run() -> int:
    initialize_database()
    existing = {b["title"] for b in bug_service.get_all_bugs()}
    added = 0
    for bug in BUGS:
        if bug["title"] in existing:
            continue
        bug_id = bug_service.log_bug(bug["module"], bug["category"], bug["title"], bug["description"],
                                       bug["severity"], bug["priority"])
        bug_service.start_progress(bug_id)
        bug_service.mark_fixed(bug_id, bug["root_cause"], bug["corrective_action"], bug["test_case"])
        added += 1
    return added


if __name__ == "__main__":
    print(f"Logged {run()} new bug(s).")
