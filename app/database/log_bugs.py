"""
Feeds the bugs found during testing into the Bug Tracker (database plus
TQM/data/defect_log.csv) and walks each one through the same workflow the
Bug screen uses. Safe to re-run: a bug whose title is already logged is skipped.

    python -m app.database.log_bugs

Bugs stop at 'Fixed'; close them in the Bug screen after re-testing.
"""
from app.database.db import get_connection, initialize_database
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
    {
        "module": "Allocation", "category": "Functional", "severity": "Low", "priority": "Medium",
        "title": "Allotment list export sorts rooms as text so A10 comes before A2",
        "description": "The exported allotment CSV orders rooms A1, A10, A2, A3 instead of A1, A2, A3, A10.",
        "root_cause": "export_allocation_list sorted by the room number string, which compares character by character.",
        "corrective_action": "Sort by block letters, then the numeric part, then the full room number (_room_order).",
        "test_case": "tests/test_bug_fixes.py::test_bug_008_*",
    },
    {
        "module": "Other", "category": "Functional", "severity": "Low", "priority": "Low",
        "title": "Quality fix rate rounds halves to even, so 12.5% shows as 12%",
        "description": "Quality summary shows 12% for 1 fixed of 8 bugs and 38% for 3 of 8, because halves round to the nearest even number.",
        "root_cause": "get_quality_summary used Python round(), which uses banker's rounding.",
        "corrective_action": "Compute the percentage with integer half-up rounding.",
        "test_case": "tests/test_bug_fixes.py::test_bug_009_*",
    },
    {
        "module": "Student", "category": "Validation", "severity": "Low", "priority": "Medium",
        "title": "Student name keeps extra spaces and tabs, and accepts names with no letters",
        "description": "'Ravi  Kumar' (two spaces) and 'Jean<tab>Luc' are stored as typed, and '...' or \"-'-\" are accepted as names.",
        "root_cause": "validate_student_name only trimmed the ends and allowed any whitespace and punctuation characters.",
        "corrective_action": "Collapse every whitespace run to one space and require at least one letter.",
        "test_case": "tests/test_bug_fixes.py::test_bug_010_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "Medium", "priority": "Medium",
        "title": "Registration number, room number and username accept look-alike non-ASCII characters",
        "description": "A registration number in Arabic-Indic digits, a username using a Cyrillic 'a', or an all-zero registration number is accepted.",
        "root_cause": "The validators used str.isalnum(), which is true for letters and digits of every script.",
        "corrective_action": "Require ASCII letters and digits (plus underscore for usernames) and reject all-zero registration numbers.",
        "test_case": "tests/test_bug_fixes.py::test_bug_011_*",
    },
    {
        "module": "UI", "category": "UI/UX", "severity": "Low", "priority": "Medium",
        "title": "Students screen loses the highlighted row after re-sorting while an edit is open",
        "description": "Select a student, change the sort order: the row is no longer highlighted but the form and Save Changes stay active, so a save changes a student the user cannot see selected.",
        "root_cause": "refresh() rebuilt the table without restoring the selection that the edit form was tied to.",
        "corrective_action": "Re-select the row of the student being edited after every refresh without overwriting the form; clear the edit state if that student is gone.",
        "test_case": "tests/test_student_screen_ui.py::test_bug_012_*",
    },
    {
        "module": "Allocation", "category": "UI/UX", "severity": "Low", "priority": "Medium",
        "title": "Allocation screen lists students who already have a room and rooms that are full",
        "description": "After allocating a room the student and room stay in the dropdowns, so the next pick can be one that the system will reject; releasing a room does not update the lists either.",
        "root_cause": "refresh_dropdowns offered every student and room, and was not re-run after allocate or release.",
        "corrective_action": "Offer only students without an active room and rooms with a free bed (showing used/capacity), and refresh the lists after allocate and release.",
        "test_case": "tests/test_allocation_screen_ui.py::test_bug_013_*",
    },
    {
        "module": "UI", "category": "UI/UX", "severity": "Low", "priority": "Medium",
        "title": "Complaint, leave and bug tables lose the selected row after every action",
        "description": "After Assign, Mark Returned or Start Progress the table refreshes and nothing is selected, so the next step (Resolve, Mark Fixed) says 'Select a complaint first' until the row is clicked again.",
        "root_cause": "The refresh methods deleted and re-inserted every row without restoring the selection.",
        "corrective_action": "Added keep_selection() in theme.py, which re-selects the same rows by ID after a refresh, and used it in the three screens.",
        "test_case": "tests/test_selection_ui.py::test_bug_014_*",
    },
    {
        "module": "UI", "category": "UI/UX", "severity": "Low", "priority": "Medium",
        "title": "Sign-up dialog still lets the request be sent again and then shows a red error",
        "description": "After 'Request sent' the Request Account button stays active; clicking it again replaces the success message with \"Username is already taken\" in red.",
        "root_cause": "Only the entry fields were disabled after success; the submit button was left enabled.",
        "corrective_action": "Disable the submit button after success and rename Cancel to Close.",
        "test_case": "tests/test_signup_ui.py::test_bug_015_*",
    },
    {
        "module": "UI", "category": "UI/UX", "severity": "Low", "priority": "Medium",
        "title": "Calendar stays on the current month after adding an event in another month",
        "description": "Adding an event dated in a different month shows 'Event added' but the calendar still shows this month, so the new event is not visible.",
        "root_cause": "on_add refreshed the calendar without moving it to the month of the new event.",
        "corrective_action": "Add CalendarWidget.show_date and call it with the saved event's date after a successful add.",
        "test_case": "tests/test_calendar_ui.py::test_bug_016_*",
    },
    {
        "module": "Allocation", "category": "Validation", "severity": "Medium", "priority": "Medium",
        "title": "Complaint, leave and allocation accept True or 1.9 as a student/room ID",
        "description": "create_complaint(1.9, ...) was saved against student 1 and True was treated as ID 1, so a malformed ID silently acted on the wrong record.",
        "root_cause": "IDs were converted with int(), which truncates floats and accepts booleans.",
        "corrective_action": "Add validate_record_id (rejects bools and non-whole floats) and use it in complaint, leave and allocation services.",
        "test_case": "tests/test_bug_fixes.py::test_bug_017_*",
    },
    {
        "module": "Allocation", "category": "Data Integrity", "severity": "Medium", "priority": "Medium",
        "title": "Student stays 'On Leave' after their room allocation is released",
        "description": "Releasing a room while the student has an open leave left the leave 'On Leave' with no active room, so the Leave screen showed a stale open leave.",
        "root_cause": "release_allocation only updated the allocation and never touched the student's open leave.",
        "corrective_action": "Close the student's open leave (Returned, with timestamp) in the same transaction as the release.",
        "test_case": "tests/test_bug_fixes.py::test_bug_018_*",
    },
    {
        "module": "Complaint", "category": "Validation", "severity": "Low", "priority": "Medium",
        "title": "Assign/resolve/release/delete actions accept True or 1.9 as a record ID",
        "description": "assign_complaint(True, ...) changed complaint 1; the same unchecked ID handling remained in the resolve, return, release, delete and approve actions after BUG-017.",
        "root_cause": "BUG-017 fixed only the create paths; the other ID-taking services still passed raw values to SQLite, which treats True as 1.",
        "corrective_action": "Apply validate_record_id at the start of every service function that takes a record ID.",
        "test_case": "tests/test_bug_fixes.py::test_bug_019_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "Medium", "priority": "Medium",
        "title": "Evidence log CSVs run user text as a spreadsheet formula",
        "description": "A bug titled =HYPERLINK(...) was written to defect_log.csv verbatim, so opening the log in Excel would evaluate it (CSV formula injection).",
        "root_cause": "Log rows were written without checking for text beginning with =, +, - or @.",
        "corrective_action": "Prefix such text with an apostrophe in the shared _append_row used by the error, audit and defect logs.",
        "test_case": "tests/test_bug_fixes.py::test_bug_020_*",
    },
    {
        "module": "Other", "category": "Validation", "severity": "Low", "priority": "Medium",
        "title": "Calendar accepts events dated year 9999 or 1900",
        "description": "add_event saved 9999-01-01 and 1900-01-01 without complaint, unlike leave dates which are limited to a window around today.",
        "root_cause": "validate_event_date only checked the YYYY-MM-DD format, not whether the date was plausible.",
        "corrective_action": "Reject event dates more than 5 years from today.",
        "test_case": "tests/test_bug_fixes.py::test_bug_021_*",
    },
    {
        "module": "Other", "category": "Data Integrity", "severity": "Low", "priority": "Low",
        "title": "Calendar lets 'Fest' and 'FEST' (or 'Fest  Night') duplicate an event on one date",
        "description": "The duplicate check compared titles exactly and extra spaces inside a title were kept, so near-identical events could be added twice on the same day.",
        "root_cause": "Titles were only trimmed at the ends and the duplicate query was case-sensitive.",
        "corrective_action": "Collapse whitespace in event titles and compare titles case-insensitively.",
        "test_case": "tests/test_bug_fixes.py::test_bug_022_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "Student session can call staff and admin services directly",
        "description": "With a Student session, add_student, delete_student, delete/add_room, release_allocation, change_password and create_user (even an Administrator account) all succeeded; only the navigation hid the screens.",
        "root_cause": "Role rules existed only in the UI navigation; most services never checked the caller's role.",
        "corrective_action": "Add session.require_roles and call it in the staff services (student, room, allocation, complaint, bug) and the admin-only account services.",
        "test_case": "tests/test_bug_fixes.py::test_bug_023_*",
    },
    {
        "module": "Allocation", "category": "Data Integrity", "severity": "High", "priority": "High",
        "title": "Simultaneous allocations can overfill a room",
        "description": "Eight allocation calls at once on a capacity-1 room put 2 students in it in testing; the capacity check and the insert were not one atomic step.",
        "root_cause": "allocate_room read the room count and then inserted under SQLite's default deferred transaction, so two callers could both pass the check.",
        "corrective_action": "Start allocate_room with BEGIN IMMEDIATE so checks and insert hold the write lock, and add unique partial indexes: one active room per student, one open leave per student.",
        "test_case": "tests/test_bug_fixes.py::test_bug_024_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "Login has no limit on wrong passwords",
        "description": "Any number of wrong passwords could be tried against an account, including the default admin account, so passwords could be guessed by repetition.",
        "root_cause": "authenticate checked the password on every call and kept no record of failures.",
        "corrective_action": "Count failed logins per account; after 5 in a row lock the account for 5 minutes (stored in the database, so a restart does not reset it), log the lockout, and reset the count on success.",
        "test_case": "tests/test_bug_fixes.py::test_bug_025_*",
    },
    {
        "module": "UI", "category": "Functional", "severity": "High", "priority": "High",
        "title": "Errors inside button/timer callbacks are never logged or shown",
        "description": "An exception raised in a Tk callback was only printed to the console: nothing reached error_logs.csv and the user saw no message, although main.run() claims to catch everything.",
        "root_cause": "Tkinter does not let callback exceptions escape mainloop, so run()'s try/except never sees them, and no report_callback_exception handler was installed.",
        "corrective_action": "Add report_tk_callback_exception to the exception handler and install it on the main window, so these errors are logged (module Application) and shown with the usual friendly message.",
        "test_case": "tests/test_callback_errors_ui.py::test_bug_026_*",
    },
    {
        "module": "Database", "category": "Functional", "severity": "High", "priority": "High",
        "title": "App exits silently when the database cannot be opened",
        "description": "With a damaged or locked database the app wrote the problem to the console and quit; started by double-click there is no console, so the user saw nothing happen.",
        "root_cause": "main.run() reported start-up failures only with print() to stderr.",
        "corrective_action": "Show the failure in a message window (with the error id and what to check) for database start-up errors and for a crash of the main window, besides logging it.",
        "test_case": "tests/test_startup_errors.py::test_bug_027_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "Default admin / admin123 account is never forced to change its password",
        "description": "The first-run Administrator is created with a known password (printed in the audit log) and nothing ever asks for it to be changed, so a deployed system keeps a publicly known admin login.",
        "root_cause": "ensure_default_admin only created the account; there was no must-change state and no first-login prompt.",
        "corrective_action": "Flag the default admin (and an existing one still using admin123) to change its password: after login the app asks for a new one before showing anything and logs out if cancelled; the default password can no longer be set again.",
        "test_case": "tests/test_bug_fixes.py::test_bug_028_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "All loaded student accounts share one known password",
        "description": "The real-data loader created every student login with the same password (Welcome123) and usernames follow the student's name, so any student could sign in as another and see or change their room, complaints, leave and details.",
        "root_cause": "Seeded accounts were created with a shared password and were never asked to change it.",
        "corrective_action": "Create loaded accounts flagged to change the password at first login (reusing the BUG-028 prompt), block Welcome123 as a new password, and flag existing accounts that still use it when the loader runs.",
        "test_case": "tests/test_bug_fixes.py::test_bug_029_*",
    },
    {
        "module": "Student", "category": "Data Integrity", "severity": "High", "priority": "High",
        "title": "Same registration number can be added twice in different letter case",
        "description": "BT24A0007 and bt24a0007 were stored as two different students, and sign-up looked the number up exactly, so the wrong record (or none) could be linked to an account.",
        "root_cause": "Registration numbers were compared and stored exactly as typed, while the database UNIQUE rule is case-sensitive.",
        "corrective_action": "Store registration numbers in upper case, compare them case-insensitively in the duplicate checks and in sign-up, and add a case-insensitive unique index (skipped if the existing data already has such duplicates).",
        "test_case": "tests/test_bug_fixes.py::test_bug_030_*",
    },
    {
        "module": "Database", "category": "Data Integrity", "severity": "Critical", "priority": "High",
        "title": "No backup: a damaged database file loses every record",
        "description": "All students, rooms, allocations, complaints and accounts live in one SQLite file with no copy anywhere. A damaged or deleted file (see BUG-027) meant losing everything.",
        "root_cause": "The application never made or offered a backup.",
        "corrective_action": "Take a verified backup once a day at start-up (kept 7 days, in app/database/backups), never back up a file that fails its integrity check, and add restore (python -m app.database.backup restore FILE) that keeps the old file as *.before_restore.",
        "test_case": "tests/test_backup.py::test_bug_031_*",
    },
    {
        "module": "Other", "category": "Security", "severity": "High", "priority": "High",
        "title": "Users cannot change their own password",
        "description": "Only an Administrator could set anyone's password. A student or warden who suspected their password was known had no way to change it, and every password an admin handed out stayed in use.",
        "root_cause": "Only an admin-side change_password existed; there was no self-service path.",
        "corrective_action": "Add change_own_password (current password required, new one must differ and not be a known default) and a 'Change password' link in the sidebar for every role.",
        "test_case": "tests/test_bug_fixes.py::test_bug_032_*",
    },
    {
        "module": "UI", "category": "Security", "severity": "High", "priority": "Medium",
        "title": "Logged-in session never times out",
        "description": "A warden or administrator who walked away from the hostel-office computer stayed logged in indefinitely, leaving every student record and the Users screen open to whoever sat down next.",
        "root_cause": "The session had no inactivity limit.",
        "corrective_action": "Track mouse and keyboard activity and log the user out after 15 minutes of inactivity (IDLE_TIMEOUT_MINUTES), recording an IdleLogout audit entry and returning to the login window.",
        "test_case": "tests/test_idle.py::test_bug_033_*",
    },
    {
        "module": "Database", "category": "Data Integrity", "severity": "High", "priority": "Medium",
        "title": "Records saved before the validation fixes are never checked",
        "description": "Rules added over time (case-insensitive registration numbers, capacity, one active room, valid contacts) only apply to new entries; bad rows already in a real database stayed unnoticed.",
        "root_cause": "Validation runs only on writes; nothing looked at existing data.",
        "corrective_action": "Add a read-only data check (python -m app.database.check_data) covering duplicate registration numbers, over-full rooms, double allocations, orphan rows, stranded leaves, unlinked accounts and values today's rules reject; run it at start-up and write each finding to the error log.",
        "test_case": "tests/test_check_data.py::test_bug_034_*",
    },
    {
        "module": "Other", "category": "Data Integrity", "severity": "High", "priority": "Medium",
        "title": "Defect log CSV has no reporter or fixer, and write failures are silent",
        "description": "defect_log.csv, the evidence file for the Bug Tracker, left out who reported and who fixed each bug (shown in the app since Batch 29), and any failure to write a row was swallowed without a trace.",
        "root_cause": "The CSV columns were fixed before reporter/fixer existed, and log_defect ignored its own errors. Simply adding columns would have made old log files reject every new row.",
        "corrective_action": "Add reported_by and fixed_by to the defect log, upgrade older log files in place (old rows keep blanks), and record a failed defect write in the error log.",
        "test_case": "tests/test_bug_fixes.py::test_bug_035_*",
    },
    {
        "module": "Allocation", "category": "Security", "severity": "High", "priority": "High",
        "title": "A student session can read every student's complaints, allocations and the allotment export",
        "description": "With a Student session, get_all_complaints, get_active_allocations and export_allocation_list returned all students' names, rooms and complaint text; only the screens were hidden. BUG-023 protected writes but not these reads.",
        "root_cause": "The read functions had no role check; privacy rules lived only in the navigation.",
        "corrective_action": "Require a staff role in get_all_complaints, get_all_leaves, get_active_allocations, export_allocation_list and get_all_bugs.",
        "test_case": "tests/test_bug_fixes.py::test_bug_036_*",
    },
]


PERSON = "Mayank"


def _fill_missing_people() -> None:
    """Bugs logged by an earlier version of this script have no reporter/fixer; set them."""
    conn = get_connection()
    try:
        conn.execute("UPDATE bugs SET reported_by = ? WHERE reported_by IS NULL", (PERSON,))
        conn.execute("UPDATE bugs SET fixed_by = ? WHERE fixed_by IS NULL AND status IN ('Fixed', 'Closed')",
                     (PERSON,))
        conn.commit()
    finally:
        conn.close()


def run() -> int:
    initialize_database()
    existing = {b["title"] for b in bug_service.get_all_bugs()}
    added = 0
    for bug in BUGS:
        if bug["title"] in existing:
            continue
        bug_id = bug_service.log_bug(bug["module"], bug["category"], bug["title"], bug["description"],
                                       bug["severity"], bug["priority"], reported_by=PERSON)
        bug_service.start_progress(bug_id)
        bug_service.mark_fixed(bug_id, bug["root_cause"], bug["corrective_action"], bug["test_case"],
                                fixed_by=PERSON)
        added += 1
    _fill_missing_people()
    return added


if __name__ == "__main__":
    print(f"Logged {run()} new bug(s).")
