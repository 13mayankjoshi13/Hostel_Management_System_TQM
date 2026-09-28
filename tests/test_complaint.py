"""
Module Tests (Q09 feature #3) — Complaint Management.

Covers create/assign/resolve and the status-transition prevention rules
from FULL PROJECT CONTEXT section 16.2 ("Invalid complaint status ->
reject"). Uses the same temp-DB / temp-CSV isolation pattern as the other
test modules — never touches the real database or TQM/data/*.csv.

Run with:
    python -m unittest discover -s tests -v
"""
import os
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, complaint_service
from app.utils.validation import ValidationError


class TestComplaintManagement(unittest.TestCase):

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
        for module in (student_service, complaint_service):
            module.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv

        initialize_database(self.tmp_db)

        self.student_id = student_service.add_student(
            "Mayank Joshi", "2410302037", "9876543210"
        )

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

    # ---- create ----

    def test_create_complaint_success(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Maintenance", "Ceiling fan is not working."
        )
        self.assertIsInstance(complaint_id, int)
        complaints = complaint_service.get_all_complaints()
        self.assertEqual(len(complaints), 1)
        self.assertEqual(complaints[0]["status"], "Open")

    def test_create_complaint_invalid_category_rejected(self):
        with self.assertRaises(ValidationError):
            complaint_service.create_complaint(self.student_id, "Spaceship", "Broken warp drive.")

    def test_create_complaint_empty_description_rejected(self):
        with self.assertRaises(ValidationError):
            complaint_service.create_complaint(self.student_id, "Noise", "")

    def test_create_complaint_nonexistent_student_rejected(self):
        with self.assertRaises(ValidationError):
            complaint_service.create_complaint(9999, "Security", "Gate lock is broken.")

    # ---- assign ----

    def test_assign_open_complaint_success(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Cleanliness", "Washroom not cleaned for 3 days."
        )
        complaint_service.assign_complaint(complaint_id, "Ramesh Kumar")
        complaints = complaint_service.get_all_complaints()
        self.assertEqual(complaints[0]["status"], "Assigned")
        self.assertEqual(complaints[0]["assigned_to"], "Ramesh Kumar")

    def test_assign_already_assigned_complaint_rejected(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Cleanliness", "Washroom not cleaned for 3 days."
        )
        complaint_service.assign_complaint(complaint_id, "Ramesh Kumar")
        with self.assertRaises(ValidationError):
            complaint_service.assign_complaint(complaint_id, "Suresh Kumar")

    def test_assign_resolved_complaint_rejected(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Food", "Food quality is poor."
        )
        complaint_service.resolve_complaint(complaint_id, "Spoke with mess contractor.")
        with self.assertRaises(ValidationError):
            complaint_service.assign_complaint(complaint_id, "Ramesh Kumar")

    def test_assign_nonexistent_complaint_rejected(self):
        with self.assertRaises(ValidationError):
            complaint_service.assign_complaint(9999, "Ramesh Kumar")

    def test_assign_empty_name_rejected(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Noise", "Loud music after 11 PM."
        )
        with self.assertRaises(ValidationError):
            complaint_service.assign_complaint(complaint_id, "")

    # ---- resolve ----

    def test_resolve_open_complaint_success(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Maintenance", "Water leakage in bathroom."
        )
        complaint_service.resolve_complaint(complaint_id, "Plumber fixed the pipe.")
        complaints = complaint_service.get_all_complaints()
        self.assertEqual(complaints[0]["status"], "Resolved")
        self.assertIsNotNone(complaints[0]["resolved_at"])

    def test_resolve_assigned_complaint_success(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Security", "Main gate not locking properly."
        )
        complaint_service.assign_complaint(complaint_id, "Security Guard Verma")
        complaint_service.resolve_complaint(complaint_id, "Lock mechanism replaced.")
        complaints = complaint_service.get_all_complaints()
        self.assertEqual(complaints[0]["status"], "Resolved")

    def test_resolve_already_resolved_complaint_rejected(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Other", "Wi-Fi is very slow."
        )
        complaint_service.resolve_complaint(complaint_id, "Router replaced.")
        with self.assertRaises(ValidationError):
            complaint_service.resolve_complaint(complaint_id, "Trying again.")

    def test_resolve_nonexistent_complaint_rejected(self):
        with self.assertRaises(ValidationError):
            complaint_service.resolve_complaint(9999, "Fixed it.")

    def test_resolve_empty_notes_rejected(self):
        complaint_id = complaint_service.create_complaint(
            self.student_id, "Maintenance", "Light not working in room."
        )
        with self.assertRaises(ValidationError):
            complaint_service.resolve_complaint(complaint_id, "")


if __name__ == "__main__":
    unittest.main()
