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

    def tearDown(self):
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

    def test_bug_log_loader_is_idempotent_and_ends_fixed(self):
        self.assertEqual(log_bugs.run(), len(log_bugs.BUGS))
        self.assertEqual(log_bugs.run(), 0)
        self.assertEqual({b["status"] for b in bug_service.get_all_bugs()}, {"Fixed"})


if __name__ == "__main__":
    unittest.main()
