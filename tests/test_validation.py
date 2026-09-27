"""
Module Tests (Q09 feature #3).

Covers validation (positive + negative cases) and student/room service
duplicate-prevention rules, using a temporary on-disk SQLite database so
tests never touch the real app/database/hostel.db.

Run with:
    python -m unittest discover -s tests -v
"""
import os
import tempfile
import unittest

from app.utils.validation import (
    validate_student_name,
    validate_registration_number,
    validate_contact_number,
    validate_room_number,
    validate_capacity,
    validate_room_type,
    ValidationError,
)
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, room_service


class TestStudentNameValidation(unittest.TestCase):
    def test_valid_name_accepted(self):
        self.assertEqual(validate_student_name("  Mayank Joshi  "), "Mayank Joshi")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValidationError):
            validate_student_name("")

    def test_whitespace_only_name_rejected(self):
        with self.assertRaises(ValidationError):
            validate_student_name("   ")

    def test_name_with_digits_rejected(self):
        with self.assertRaises(ValidationError):
            validate_student_name("Mayank123")


class TestRegistrationNumberValidation(unittest.TestCase):
    def test_valid_reg_no_accepted(self):
        self.assertEqual(validate_registration_number("2410302037"), "2410302037")

    def test_empty_reg_no_rejected(self):
        with self.assertRaises(ValidationError):
            validate_registration_number("")

    def test_reg_no_with_special_characters_rejected(self):
        with self.assertRaises(ValidationError):
            validate_registration_number("2410-302037")


class TestContactNumberValidation(unittest.TestCase):
    def test_valid_contact_accepted(self):
        self.assertEqual(validate_contact_number("9876543210"), "9876543210")

    def test_short_contact_rejected(self):
        with self.assertRaises(ValidationError):
            validate_contact_number("12345")

    def test_non_numeric_contact_rejected(self):
        with self.assertRaises(ValidationError):
            validate_contact_number("98765abcde")


class TestRoomValidation(unittest.TestCase):
    def test_valid_room_number_accepted(self):
        self.assertEqual(validate_room_number("A101"), "A101")

    def test_empty_room_number_rejected(self):
        with self.assertRaises(ValidationError):
            validate_room_number("")

    def test_zero_capacity_rejected(self):
        with self.assertRaises(ValidationError):
            validate_capacity(0)

    def test_negative_capacity_rejected(self):
        with self.assertRaises(ValidationError):
            validate_capacity(-2)

    def test_non_numeric_capacity_rejected(self):
        with self.assertRaises(ValidationError):
            validate_capacity("abc")

    def test_valid_capacity_accepted(self):
        self.assertEqual(validate_capacity("3"), 3)

    def test_valid_room_type_accepted(self):
        self.assertEqual(validate_room_type("double"), "Double")

    def test_invalid_room_type_rejected(self):
        with self.assertRaises(ValidationError):
            validate_room_type("Palace")


class TestServiceLayerWithTempDatabase(unittest.TestCase):
    """
    Uses a temporary SQLite file so these tests never touch the real
    application database, and monkey-patches config.DATABASE_PATH for
    the duration of each test.
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        self.tmp_error_csv = os.path.join(self.tmp_dir, "test_error_logs.csv")
        self.tmp_audit_csv = os.path.join(self.tmp_dir, "test_audit_logs.csv")

        import app.config as config
        import app.utils.logging_service as logging_service

        # Redirect the database AND the quality-evidence CSVs to a temp
        # location for the duration of the test. Without this, running
        # the test suite would write fake rows into the real
        # TQM/data/audit_logs.csv and error_logs.csv — which would be
        # fabricated quality evidence, exactly what the project must not do.
        self._original_db_path = config.DATABASE_PATH
        self._original_error_csv = logging_service.ERROR_LOG_CSV
        self._original_audit_csv = logging_service.AUDIT_LOG_CSV

        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        student_service.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db
        room_service.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv

        initialize_database(self.tmp_db)

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

    def test_add_student_success(self):
        student_id = student_service.add_student("Mayank Joshi", "2410302037", "9876543210")
        self.assertIsInstance(student_id, int)
        students = student_service.get_all_students()
        self.assertEqual(len(students), 1)

    def test_add_duplicate_registration_number_rejected(self):
        student_service.add_student("Mayank Joshi", "2410302037", "9876543210")
        with self.assertRaises(ValidationError):
            student_service.add_student("Another Student", "2410302037", "9123456780")

    def test_add_room_success(self):
        room_id = room_service.add_room("A101", "Single", 1)
        self.assertIsInstance(room_id, int)
        rooms = room_service.get_all_rooms()
        self.assertEqual(len(rooms), 1)

    def test_add_duplicate_room_number_rejected(self):
        room_service.add_room("A101", "Single", 1)
        with self.assertRaises(ValidationError):
            room_service.add_room("A101", "Double", 2)


if __name__ == "__main__":
    unittest.main()
