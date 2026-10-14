"""Regression tests — one block per bug in the Bug Tracker (see docs/bugs/)."""
import os
import tempfile
import unittest

from app.database import db as db_module, log_bugs
from app.database.db import initialize_database
from app.services import room_service, bug_service, student_service
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

    def test_bug_log_loader_is_idempotent_and_ends_fixed(self):
        self.assertEqual(log_bugs.run(), len(log_bugs.BUGS))
        self.assertEqual(log_bugs.run(), 0)
        self.assertEqual({b["status"] for b in bug_service.get_all_bugs()}, {"Fixed"})


if __name__ == "__main__":
    unittest.main()
