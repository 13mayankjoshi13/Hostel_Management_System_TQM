"""
Module Tests (Q09 feature #3) — Room Allocation.

Covers the full prevention pipeline from FULL PROJECT CONTEXT section 6:
Select Student -> Check Student -> Select Room -> Check Room Exists ->
Check Capacity -> Check Existing Allocation -> Allocate.

Uses a temporary on-disk SQLite database and temporary log CSVs so these
tests never touch the real app/database/hostel.db or TQM/data/*.csv.

Run with:
    python -m unittest discover -s tests -v
"""
import os
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, room_service, allocation_service
from app.utils.validation import ValidationError


class TestRoomAllocation(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        self.tmp_error_csv = os.path.join(self.tmp_dir, "test_error_logs.csv")
        self.tmp_audit_csv = os.path.join(self.tmp_dir, "test_audit_logs.csv")

        import app.config as config
        import app.utils.logging_service as logging_service

        self._original_db_path = config.DATABASE_PATH
        self._original_error_csv = logging_service.ERROR_LOG_CSV
        self._original_audit_csv = logging_service.AUDIT_LOG_CSV

        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        for module in (student_service, room_service, allocation_service):
            module.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv

        initialize_database(self.tmp_db)

        self.student_id = student_service.add_student(
            "Mayank Joshi", "2410302037", "9876543210"
        )
        self.room_id = room_service.add_room("A101", "Single", 1)
        self.double_room_id = room_service.add_room("A102", "Double", 2)

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as logging_service

        config.DATABASE_PATH = self._original_db_path
        db_module.DATABASE_PATH = self._original_db_path
        logging_service.ERROR_LOG_CSV = self._original_error_csv
        logging_service.AUDIT_LOG_CSV = self._original_audit_csv

        for path in (self.tmp_db, self.tmp_error_csv, self.tmp_audit_csv):
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.tmp_dir)

    def test_successful_allocation(self):
        allocation_id = allocation_service.allocate_room(self.student_id, self.room_id)
        self.assertIsInstance(allocation_id, int)
        active = allocation_service.get_active_allocations()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["student_id"], self.student_id)

    def test_nonexistent_student_rejected(self):
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(9999, self.room_id)

    def test_nonexistent_room_rejected(self):
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(self.student_id, 9999)

    def test_room_at_capacity_rejected(self):
        # Single room, capacity 1 — first allocation succeeds.
        second_student_id = student_service.add_student(
            "Second Student", "2410302038", "9876543211"
        )
        allocation_service.allocate_room(self.student_id, self.room_id)
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(second_student_id, self.room_id)

    def test_duplicate_active_allocation_rejected(self):
        allocation_service.allocate_room(self.student_id, self.room_id)
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(self.student_id, self.double_room_id)

    def test_double_room_allows_two_active_allocations(self):
        second_student_id = student_service.add_student(
            "Second Student", "2410302038", "9876543211"
        )
        allocation_service.allocate_room(self.student_id, self.double_room_id)
        allocation_service.allocate_room(second_student_id, self.double_room_id)
        active = allocation_service.get_active_allocations()
        self.assertEqual(len(active), 2)

    def test_release_allocation_frees_room(self):
        allocation_id = allocation_service.allocate_room(self.student_id, self.room_id)
        allocation_service.release_allocation(allocation_id)
        active = allocation_service.get_active_allocations()
        self.assertEqual(len(active), 0)

        # Room should now accept a new allocation again.
        second_student_id = student_service.add_student(
            "Second Student", "2410302038", "9876543211"
        )
        new_allocation_id = allocation_service.allocate_room(second_student_id, self.room_id)
        self.assertIsInstance(new_allocation_id, int)

    def test_release_nonexistent_allocation_rejected(self):
        with self.assertRaises(ValidationError):
            allocation_service.release_allocation(9999)

    def test_release_already_released_allocation_rejected(self):
        allocation_id = allocation_service.allocate_room(self.student_id, self.room_id)
        allocation_service.release_allocation(allocation_id)
        with self.assertRaises(ValidationError):
            allocation_service.release_allocation(allocation_id)


if __name__ == "__main__":
    unittest.main()
