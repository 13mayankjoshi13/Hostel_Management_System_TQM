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
    {
        "module": "Room", "category": "Validation", "severity": "Low", "priority": "Low",
        "title": "Room capacity silently converts 1.5 and True to 1",
        "description": "add_room(\"R1\", \"Single\", 1.5) or capacity True creates a room with capacity 1 instead of rejecting the input.",
        "root_cause": "validate_capacity called int() directly, which truncates floats and treats bool as 0/1.",
        "corrective_action": "Reject bool and non-integral floats before int() in validate_capacity.",
        "test_case": "tests/test_bug_fixes.py::test_bug_004_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "Usernames Bob and bob can both be created and login is case-sensitive",
        "description": "Two accounts whose usernames differ only in case can exist, so look-alike accounts are possible and logging in as BOB fails.",
        "root_cause": "create_user and authenticate compared usernames with exact case-sensitive matching.",
        "corrective_action": "Compare usernames with LOWER() in create_user (duplicate check) and authenticate (lookup).",
        "test_case": "tests/test_bug_fixes.py::test_bug_005_*",
    },
    {
        "module": "Other", "category": "Validation", "severity": "Medium", "priority": "Medium",
        "title": "Leave dates accept impossible ranges such as year 1900 or multi-year leaves",
        "description": "Leave screen accepts a leave dated 1900-01-01 or one lasting 5 years, which makes leave tracking meaningless.",
        "root_cause": "validate_leave_dates only checked the format and that the end is not before the start.",
        "corrective_action": "Limit a leave to 180 days and require dates within one year of today.",
        "test_case": "tests/test_bug_fixes.py::test_bug_006_*",
    },
    {
        "module": "Other", "category": "Functional", "severity": "Medium", "priority": "Medium",
        "title": "Deleting a student or room that is in use shows a generic database error",
        "description": "Deleting a student or room with allocations, complaints, leaves or an account fails with 'database error' and logs a High error; deleting a missing id reports success.",
        "root_cause": "delete_student and delete_room relied on the foreign-key failure instead of checking dependent records first.",
        "corrective_action": "Check existence and dependent records before deleting and raise a specific message; no database error is triggered.",
        "test_case": "tests/test_bug_fixes.py::test_bug_007_*",
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
