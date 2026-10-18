"""Regression tests — one block per bug in the Bug Tracker (see docs/bugs/)."""
import os
import tempfile
import unittest

from datetime import date, timedelta

from app.database import db as db_module, log_bugs
from app.database.db import initialize_database
from app.services import room_service, bug_service, student_service, auth_service, allocation_service
from app.utils.validation import ValidationError


class TestBugFixes(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "t.db")
        import app.config as config
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV, ls.DEFECT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = self.db
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        ls.DEFECT_LOG_CSV = os.path.join(self.tmp, "d.csv")
        initialize_database(self.db)
        from app.utils import session
        session.clear_session()

    def tearDown(self):
        from app.utils import session
        session.clear_session()
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV, ls.DEFECT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_001_mismatched_type_and_capacity_rejected(self):
        for room_type, capacity in (("Single", 5), ("Double", 1), ("Triple", 2), ("Dormitory", 2)):
            with self.assertRaises(ValidationError, msg=f"{room_type}/{capacity}"):
                room_service.add_room("R1", room_type, capacity)

    def test_bug_001_matching_type_and_capacity_accepted(self):
        for number, (room_type, capacity) in enumerate((("Single", 1), ("Double", 2), ("Triple", 3), ("Dormitory", 8))):
            self.assertTrue(room_service.add_room(f"R{number}", room_type, capacity))

    def test_bug_002_invalid_mobile_numbers_rejected(self):
        for number in ("0123456789", "5123456789", "1234567890", "\u0669\u0668\u0667\u0666\u0665\u0664\u0663\u0662\u0661\u0660"):
            with self.assertRaises(ValidationError, msg=number):
                student_service.add_student("Test Name", "2410302001", number)

    def test_bug_002_valid_mobile_numbers_accepted(self):
        for index, number in enumerate(("6123456789", "7123456789", "8123456789", "9123456789")):
            self.assertTrue(student_service.add_student(f"Test Name", f"241030200{index}", number))

    def test_bug_003_room_number_case_duplicate_rejected(self):
        room_service.add_room("Q1", "Single", 1)
        with self.assertRaises(ValidationError):
            room_service.add_room("q1", "Single", 1)

    def test_bug_003_room_number_stored_upper_case(self):
        room_service.add_room("b12", "Single", 1)
        self.assertEqual(room_service.get_all_rooms()[0]["room_number"], "B12")

    def test_bug_003_existing_mixed_case_room_still_blocks_duplicate(self):
        import sqlite3
        conn = sqlite3.connect(self.db)
        conn.execute("INSERT INTO rooms (room_number, room_type, capacity) VALUES ('c5', 'Single', 1)")
        conn.commit()
        conn.close()
        with self.assertRaises(ValidationError):
            room_service.add_room("C5", "Single", 1)

    def test_bug_004_non_whole_capacity_rejected(self):
        for capacity in (1.5, True, False, "1.5", None):
            with self.assertRaises(ValidationError, msg=repr(capacity)):
                room_service.add_room("R1", "Single", capacity)

    def test_bug_004_whole_capacity_forms_accepted(self):
        for number, capacity in enumerate((1, "1", 1.0)):
            self.assertTrue(room_service.add_room(f"R{number}", "Single", capacity))

    def test_bug_005_username_case_duplicate_rejected(self):
        auth_service.create_user("Bob", "Secret123", "Staff")
        with self.assertRaises(ValidationError):
            auth_service.create_user("bob", "Secret123", "Staff")

    def test_bug_005_login_ignores_username_case(self):
        auth_service.create_user("Bob", "Secret123", "Staff")
        self.assertEqual(auth_service.authenticate("BOB", "Secret123")["username"], "Bob")

    def test_bug_005_wrong_password_still_rejected(self):
        auth_service.create_user("Bob", "Secret123", "Staff")
        with self.assertRaises(ValidationError):
            auth_service.authenticate("bob", "Wrong123")

    def test_bug_006_impossible_leave_dates_rejected(self):
        from app.utils.validation import validate_leave_dates
        today = date.today()
        iso = lambda n: (today + timedelta(days=n)).isoformat()
        for start, end in (("1900-01-01", "1900-01-02"), (iso(0), iso(181)), (iso(-400), iso(-399)), (iso(400), iso(401))):
            with self.assertRaises(ValidationError, msg=f"{start}..{end}"):
                validate_leave_dates(start, end)

    def test_bug_006_normal_leave_dates_accepted(self):
        from app.utils.validation import validate_leave_dates
        today = date.today()
        self.assertEqual(validate_leave_dates((today - timedelta(days=3)).isoformat(),
                                               (today + timedelta(days=177)).isoformat())[0],
                         (today - timedelta(days=3)).isoformat())

    def _error_rows(self):
        import app.utils.logging_service as ls
        return open(ls.ERROR_LOG_CSV).read().count("\n") if os.path.exists(ls.ERROR_LOG_CSV) else 0

    def test_bug_007_in_use_student_and_room_give_specific_message(self):
        sid = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        rid = room_service.add_room("A1", "Single", 1)
        allocation_service.allocate_room(sid, rid)
        with self.assertRaisesRegex(ValidationError, "active room allocation"):
            student_service.delete_student(sid)
        with self.assertRaisesRegex(ValidationError, "allocated"):
            room_service.delete_room(rid)
        self.assertEqual(self._error_rows(), 0)

    def test_bug_007_history_blocks_delete_with_message(self):
        sid = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        rid = room_service.add_room("A1", "Single", 1)
        aid = allocation_service.allocate_room(sid, rid)
        allocation_service.release_allocation(aid)
        with self.assertRaisesRegex(ValidationError, "records"):
            student_service.delete_student(sid)
        with self.assertRaisesRegex(ValidationError, "history"):
            room_service.delete_room(rid)

    def test_bug_007_missing_ids_and_unused_records(self):
        with self.assertRaisesRegex(ValidationError, "does not exist"):
            student_service.delete_student(999)
        with self.assertRaisesRegex(ValidationError, "does not exist"):
            room_service.delete_room(999)
        sid = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        rid = room_service.add_room("A1", "Single", 1)
        student_service.delete_student(sid)
        room_service.delete_room(rid)
        self.assertEqual((student_service.get_all_students(), room_service.get_all_rooms()), ([], []))

    def test_bug_008_export_rooms_in_natural_order(self):
        import csv
        for i, number in enumerate(("B3", "A10", "A2", "A1", "AB1")):
            allocation_service.allocate_room(student_service.add_student(f"Stud {chr(65 + i)}x", f"24103020{i:02d}", "9876543210"),
                                             room_service.add_room(number, "Single", 1))
        path = os.path.join(self.tmp, "x.csv")
        allocation_service.export_allocation_list(path)
        with open(path, newline="") as f:
            rooms = [row[0] for row in list(csv.reader(f))[1:]]
        self.assertEqual(rooms, ["A1", "A2", "A10", "AB1", "B3"])

    def test_bug_009_fix_rate_rounds_half_up(self):
        from app.services.quality_service import get_quality_summary
        for expected, fixed, total in ((13, 1, 8), (38, 3, 8), (0, 0, 8), (100, 8, 8), (33, 1, 3), (67, 2, 3)):
            ids = [bug_service.log_bug("Room", "Validation", f"Bug number {i}", "description text", "Low", "Low")
                   for i in range(total)]
            for bug_id in ids[:fixed]:
                bug_service.start_progress(bug_id)
                bug_service.mark_fixed(bug_id, "root cause x", "action taken", "test x")
            self.assertEqual(get_quality_summary()["fix_rate_pct"], expected, f"{fixed}/{total}")
            conn = db_module.get_connection()
            conn.execute("DELETE FROM bugs")
            conn.commit()
            conn.close()

    def test_bug_009_no_bugs_gives_zero(self):
        from app.services.quality_service import get_quality_summary
        self.assertEqual(get_quality_summary()["fix_rate_pct"], 0)

    def test_bug_010_name_whitespace_normalised(self):
        from app.utils.validation import validate_student_name
        self.assertEqual(validate_student_name("  ravi   kumar "), "ravi kumar")
        self.assertEqual(validate_student_name("Jean\tLuc"), "Jean Luc")
        self.assertEqual(validate_student_name("Anne-Marie O'Brien"), "Anne-Marie O'Brien")

    def test_bug_010_names_without_letters_rejected(self):
        from app.utils.validation import validate_student_name
        for name in ("...", "-'-", ". .", "  \t "):
            with self.assertRaises(ValidationError, msg=repr(name)):
                validate_student_name(name)

    def test_bug_010_spacing_variants_stored_once(self):
        student_service.add_student("Ravi  Kumar", "2410302001", "9876543210")
        self.assertEqual(student_service.get_all_students()[0]["name"], "Ravi Kumar")

    def test_bug_011_non_ascii_identifiers_rejected(self):
        from app.utils.validation import validate_registration_number, validate_room_number, validate_username
        arabic_digits = "\u0662\u0664\u0661\u0660\u0663\u0660\u0662\u0660\u0663\u0667"
        cyrillic_a = "\u0430dmin"
        for check, value in ((validate_registration_number, arabic_digits),
                             (validate_registration_number, "0000000000"),
                             (validate_room_number, "\u0410101"),
                             (validate_username, cyrillic_a)):
            with self.assertRaises(ValidationError, msg=repr(value)):
                check(value)

    def test_bug_011_ascii_identifiers_still_accepted(self):
        from app.utils.validation import validate_registration_number, validate_room_number, validate_username
        self.assertEqual(validate_registration_number("2410302037"), "2410302037")
        self.assertEqual(validate_registration_number("BT24A0007"), "BT24A0007")
        self.assertEqual(validate_room_number("a101"), "A101")
        self.assertEqual(validate_username("mayank_joshi"), "mayank_joshi")

    def test_bug_017_record_ids_reject_bool_and_fractions(self):
        from app.services import complaint_service, leave_service
        sid = student_service.add_student("Test Kid", "2410302099", "9876500000")
        rid = room_service.add_room("A101", "Double", 2)
        for bad in (True, 1.9):
            with self.assertRaises(ValidationError):
                complaint_service.create_complaint(bad, "Maintenance", "Tap is leaking badly")
            with self.assertRaises(ValidationError):
                leave_service.record_leave(bad, "2026-10-20", "2026-10-22", "Family function")
            with self.assertRaises(ValidationError):
                allocation_service.allocate_room(bad, rid)
            with self.assertRaises(ValidationError):
                allocation_service.allocate_room(sid, bad)
        self.assertEqual(complaint_service.get_all_complaints(), [])
        self.assertIsInstance(complaint_service.create_complaint(sid, "Maintenance", "Tap is leaking badly"), int)
        self.assertIsInstance(complaint_service.create_complaint(str(sid), "Maintenance", "Light is not working"), int)

    def test_bug_018_releasing_a_room_closes_the_open_leave(self):
        from app.services import leave_service
        sid = student_service.add_student("Test Kid", "2410302099", "9876500000")
        rid = room_service.add_room("A101", "Double", 2)
        aid = allocation_service.allocate_room(sid, rid)
        today = date.today()
        leave_service.record_leave(sid, (today + timedelta(1)).isoformat(),
                                   (today + timedelta(3)).isoformat(), "Family function")
        allocation_service.release_allocation(aid)
        self.assertEqual([lv["status"] for lv in leave_service.get_all_leaves()], ["Returned"])

    def test_bug_019_status_and_delete_actions_reject_bool_and_fraction_ids(self):
        from app.services import complaint_service, leave_service
        sid = student_service.add_student("Test Kid", "2410302099", "9876500000")
        complaint_service.create_complaint(sid, "Maintenance", "Tap is leaking badly")
        calls = [
            lambda b: complaint_service.assign_complaint(b, "Ravi"),
            lambda b: complaint_service.resolve_complaint(b, "Fixed the tap"),
            lambda b: leave_service.mark_returned(b),
            lambda b: allocation_service.release_allocation(b),
            lambda b: room_service.delete_room(b),
            lambda b: student_service.delete_student(b),
            lambda b: student_service.update_student(b, "New Name", "2410302098", "9876500001"),
            lambda b: bug_service.close_bug(b),
        ]
        for call in calls:
            for bad in (True, 1.9):
                with self.assertRaises(ValidationError):
                    call(bad)
        self.assertEqual(complaint_service.get_all_complaints()[0]["status"], "Open")

    def test_bug_020_log_csv_neutralises_formula_text(self):
        import csv
        import app.utils.logging_service as ls
        bug_service.log_bug("Room", "Validation", '=HYPERLINK("http://x","a")',
                            "+1 description long enough here", "Medium", "Medium")
        with open(ls.DEFECT_LOG_CSV, newline="", encoding="utf-8") as f:
            row = next(csv.DictReader(f))
        self.assertEqual(row["title"], "'=HYPERLINK(\"http://x\",\"a\")")
        self.assertEqual(row["description"], "'+1 description long enough here")
        self.assertEqual(row["date"][:2], "20")

    def test_bug_021_event_dates_limited_to_a_sensible_window(self):
        from app.services import event_service
        from app.utils import session
        session.set_session("admin", "Administrator")
        for bad in ("9999-01-01", "1900-01-01"):
            with self.assertRaises(ValidationError):
                event_service.add_event(bad, "Far Away Fest", "Hostel Event")
        near = date(date.today().year + 1, 3, 3).isoformat()
        self.assertIsInstance(event_service.add_event(near, "Spring Fest", "Hostel Event"), int)

    def test_bug_022_event_titles_normalised_and_duplicates_ignore_case(self):
        from app.services import event_service
        from app.utils import session
        session.set_session("admin", "Administrator")
        day = date(date.today().year + 1, 3, 3).isoformat()
        event_service.add_event(day, "  Spring   Fest ", "Hostel Event")
        self.assertEqual(event_service.get_all_events()[-1]["title"], "Spring Fest")
        for dup in ("SPRING FEST", "spring  fest"):
            with self.assertRaises(ValidationError):
                event_service.add_event(day, dup, "Exam")

    def test_bug_023_services_enforce_roles(self):
        from app.services import auth_service as auth, complaint_service
        from app.utils import session
        session.set_session("admin", "Administrator")
        sid = student_service.add_student("Test Kid", "2410302099", "9876500000")
        rid = room_service.add_room("A101", "Double", 2)
        aid = allocation_service.allocate_room(sid, rid)
        session.set_session("stu", "Student", sid)
        blocked = [
            lambda: student_service.add_student("Evil Kid", "2410302090", "9876500002"),
            lambda: student_service.get_all_students(),
            lambda: student_service.delete_student(sid),
            lambda: room_service.add_room("B1", "Single", 1),
            lambda: room_service.delete_room(rid),
            lambda: allocation_service.release_allocation(aid),
            lambda: auth.create_user("hax", "Secret123", "Administrator"),
            lambda: auth.change_password(1, "Secret123"),
            lambda: auth.list_users(),
            lambda: complaint_service.resolve_complaint(1, "Done and dusted"),
            lambda: bug_service.log_bug("Room", "Validation", "Student made bug", "A student logging a bug here", "Low", "Low"),
        ]
        for call in blocked:
            with self.assertRaises(ValidationError):
                call()
        session.set_session("warden", "Warden")
        self.assertEqual(len(student_service.get_all_students()), 1)
        with self.assertRaises(ValidationError):
            auth.create_user("hax", "Secret123", "Administrator")
        session.set_session("admin", "Administrator")
        self.assertIsInstance(auth.create_user("boss", "Secret123", "Warden"), int)

    def test_bug_log_loader_is_idempotent_and_ends_fixed(self):
        self.assertEqual(log_bugs.run(), len(log_bugs.BUGS))
        self.assertEqual(log_bugs.run(), 0)
        self.assertEqual({b["status"] for b in bug_service.get_all_bugs()}, {"Fixed"})


if __name__ == "__main__":
    unittest.main()
