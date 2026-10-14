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
