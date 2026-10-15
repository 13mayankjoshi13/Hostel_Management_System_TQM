"""Module Tests (Q09 feature #3) — Leave Tracking, allotment export, Washroom category."""
import csv
import os
import tempfile
import unittest
from datetime import date, timedelta

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, room_service, allocation_service, leave_service, complaint_service
from app.utils.validation import ValidationError


def _day(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


class TestLeave(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        self.tmp_error_csv = os.path.join(self.tmp_dir, "test_error_logs.csv")
        self.tmp_audit_csv = os.path.join(self.tmp_dir, "test_audit_logs.csv")

        import app.config as config
        import app.utils.logging_service as logging_service

        self._original = (config.DATABASE_PATH, logging_service.ERROR_LOG_CSV, logging_service.AUDIT_LOG_CSV)
        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv
        initialize_database(self.tmp_db)

        self.student_id = student_service.add_student("Mayank Joshi", "2410302037", "9876543210")
        self.room_id = room_service.add_room("A101", "Single", 1)
        self.other_student = student_service.add_student("Test Student", "2410302099", "9876543211")

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as logging_service

        config.DATABASE_PATH, logging_service.ERROR_LOG_CSV, logging_service.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        for name in os.listdir(self.tmp_dir):
            os.remove(os.path.join(self.tmp_dir, name))
        os.rmdir(self.tmp_dir)

    def _allocate(self):
        allocation_service.allocate_room(self.student_id, self.room_id)

    def test_record_leave_success_stores_room(self):
        self._allocate()
        leave_service.record_leave(self.student_id, _day(-9), _day(-5), "Family function")
        leave = leave_service.get_all_leaves()[0]
        self.assertEqual((leave["room_number"], leave["status"]), ("A101", "On Leave"))

    def test_leave_requires_active_allocation(self):
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.student_id, _day(-9), _day(-5), "Home")

    def test_invalid_date_format_rejected(self):
        self._allocate()
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.student_id, "01-10-2026", _day(-5), "Home")

    def test_end_before_start_rejected(self):
        self._allocate()
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.student_id, _day(-5), _day(-9), "Home")

    def test_empty_reason_rejected(self):
        self._allocate()
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.student_id, _day(-9), _day(-5), "  ")

    def test_second_open_leave_rejected(self):
        self._allocate()
        leave_service.record_leave(self.student_id, _day(-9), _day(-5), "Home")
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.student_id, _day(0), _day(2), "Trip")

    def test_mark_returned_then_new_leave_allowed(self):
        self._allocate()
        leave_id = leave_service.record_leave(self.student_id, _day(-9), _day(-5), "Home")
        leave_service.mark_returned(leave_id)
        self.assertEqual(leave_service.get_all_leaves()[0]["status"], "Returned")
        leave_service.record_leave(self.student_id, _day(0), _day(2), "Trip")

    def test_mark_returned_twice_rejected(self):
        self._allocate()
        leave_id = leave_service.record_leave(self.student_id, _day(-9), _day(-5), "Home")
        leave_service.mark_returned(leave_id)
        with self.assertRaises(ValidationError):
            leave_service.mark_returned(leave_id)

    def test_mark_returned_unknown_leave(self):
        with self.assertRaises(ValidationError):
            leave_service.mark_returned(999)

    def test_export_allocation_list_writes_csv(self):
        self._allocate()
        path = os.path.join(self.tmp_dir, "list.csv")
        self.assertEqual(allocation_service.export_allocation_list(path), 1)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["Room", "Type", "Student", "Allocated At"])
        self.assertEqual(rows[1][:3], ["A101", "Single", "Mayank Joshi"])

    def test_export_to_bad_path_rejected(self):
        with self.assertRaises(ValidationError):
            allocation_service.export_allocation_list(os.path.join(self.tmp_dir, "missing", "x.csv"))

    def test_washroom_complaint_category_accepted(self):
        complaint_id = complaint_service.create_complaint(self.student_id, "Washroom", "Tap is leaking badly.")
        self.assertGreater(complaint_id, 0)


if __name__ == "__main__":
    unittest.main()
