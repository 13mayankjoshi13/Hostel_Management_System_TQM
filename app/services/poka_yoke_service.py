"""
Poka-Yoke register: the error-proofing controls that exist in the application, each pointing at the
test that proves it. A test checks every reference, so an entry cannot outlive its evidence.
"""
import os
import re

from app.utils import session

PREVENT, DETECT = "Prevention", "Detection"

CONTROLS = [
    ("Allocation", PREVENT, "A full room cannot be allocated", "tests/test_allocation.py", "test_room_at_capacity_rejected"),
    ("Allocation", PREVENT, "A student holds only one active room", "tests/test_allocation.py", "test_duplicate_active_allocation_rejected"),
    ("Allocation", PREVENT, "A Boys room only takes male students, a Girls room only female", "tests/test_notices_attendance.py", "test_hostel_gender_rule_in_allocation"),
    ("Attendance", PREVENT, "No future dates and no marking on approved-leave days", "tests/test_notices_attendance.py", "test_attendance_marking_and_leave"),
    ("Notices", PREVENT, "A student only receives notices meant for them", "tests/test_notices_attendance.py", "test_notice_audiences"),
    ("Hostel map", PREVENT, "Students cannot see who stays in a room", "tests/test_home.py", "test_floor_plan_hides_names_from_students"),
    ("Fines", PREVENT, "Amounts are parsed to paise and bad amounts are refused", "tests/test_fines.py", "test_amount_is_parsed_to_paise_and_bad_amounts_are_rejected"),
    ("Fines", PREVENT, "A fine is paid only when Razorpay confirms the matching amount", "tests/test_fines.py", "test_payment_that_does_not_match_is_not_accepted"),
    ("Fines", PREVENT, "One Razorpay payment cannot settle two fines", "tests/test_fines.py", "test_one_razorpay_payment_cannot_settle_two_fines"),
    ("Fines", PREVENT, "A student cannot pay or print for another student", "tests/test_fines.py", "test_a_student_cannot_pay_or_print_for_another_student"),
    ("Roles", PREVENT, "Services refuse what the menus hide", "tests/test_roles.py", "test_services_enforce_what_the_menus_hide"),
    ("Login", PREVENT, "A wrong password never reveals which panel an account belongs to", "tests/test_login_panels.py", "test_wrong_panel_with_wrong_password_reveals_nothing_and_unknown_panel_is_refused"),
    ("Settings", PREVENT, "Accent colours too light for white text are refused", "tests/test_settings.py", "test_appearance_validation"),
    ("Logging", DETECT, "The audit log is append-only and never crashes the app", "tests/test_logging.py", "test_audit_log_is_append_only"),
    ("Session", DETECT, "Idle sessions are logged out and recorded", "tests/test_idle.py", "test_bug_033_idle_session_is_logged_out_but_active_one_is_not"),
    ("Database", DETECT, "A daily backup is made and can be restored", "tests/test_backup.py", "test_bug_031_backup_is_created_once_per_day_and_restorable"),
]


def list_controls(root: str = None) -> list:
    session.require_roles(session.ADMIN_ROLES, "view the Poka-Yoke register")
    root = root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = []
    for area, kind, control, path, test in CONTROLS:
        full = os.path.join(root, path)
        try:
            with open(full, encoding="utf-8") as f:
                text = f.read()
            proven = bool(re.search(rf"def {re.escape(test)}\b", text)) if test else True
        except OSError:
            proven = False
        result.append({"area": area, "kind": kind, "control": control, "test": f"{path}" + (f"::{test}" if test else ""),
                       "proven": proven})
    return result
