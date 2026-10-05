"""
Module Tests (Q09 feature #3) — Bug Tracker (Q09 feature #4).

Covers log/start_progress/mark_fixed/close_bug and the forward-only
status pipeline, using the same temp-DB / temp-CSV isolation pattern as
every other test module — never touches the real database or
TQM/data/*.csv.

Run with:
    python -m unittest discover -s tests -v
"""
import os
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import bug_service
from app.utils.validation import ValidationError


class TestBugTracker(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        self.tmp_error_csv = os.path.join(self.tmp_dir, "test_error_logs.csv")
        self.tmp_audit_csv = os.path.join(self.tmp_dir, "test_audit_logs.csv")
        self.tmp_defect_csv = os.path.join(self.tmp_dir, "test_defect_log.csv")

        import app.config as config
        import app.utils.logging_service as logging_service

        self._original_db_path = config.DATABASE_PATH
        self._original_error_csv = logging_service.ERROR_LOG_CSV
        self._original_audit_csv = logging_service.AUDIT_LOG_CSV
        self._original_defect_csv = logging_service.DEFECT_LOG_CSV

        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        bug_service.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv
        logging_service.DEFECT_LOG_CSV = self.tmp_defect_csv

        initialize_database(self.tmp_db)

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as logging_service

        config.DATABASE_PATH = self._original_db_path
        db_module.DATABASE_PATH = self._original_db_path
        logging_service.ERROR_LOG_CSV = self._original_error_csv
        logging_service.AUDIT_LOG_CSV = self._original_audit_csv
        logging_service.DEFECT_LOG_CSV = self._original_defect_csv

        for path in (self.tmp_db, self.tmp_error_csv, self.tmp_audit_csv, self.tmp_defect_csv):
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.tmp_dir)

    def _log_sample_bug(self):
        return bug_service.log_bug(
            "Allocation", "Functional", "Capacity check off by one",
            "Room accepted one more student than its capacity.",
            "High", "High",
        )

    # ---- log_bug ----

    def test_log_bug_success(self):
        bug_id = self._log_sample_bug()
        self.assertIsInstance(bug_id, int)
        bugs = bug_service.get_all_bugs()
        self.assertEqual(len(bugs), 1)
        self.assertEqual(bugs[0]["status"], "Open")

    def test_log_bug_invalid_module_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.log_bug("Spaceship", "Functional", "Title here", "Description here",
                                 "High", "High")

    def test_log_bug_invalid_category_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.log_bug("Room", "Haunting", "Title here", "Description here",
                                 "High", "High")

    def test_log_bug_short_title_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.log_bug("Room", "Functional", "Bad", "Description here", "High", "High")

    def test_log_bug_invalid_severity_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.log_bug("Room", "Functional", "Title here", "Description here",
                                 "Catastrophic", "High")

    def test_log_bug_invalid_priority_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.log_bug("Room", "Functional", "Title here", "Description here",
                                 "High", "Urgent")

    # ---- start_progress ----

    def test_start_progress_success(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        bugs = bug_service.get_all_bugs()
        self.assertEqual(bugs[0]["status"], "In Progress")

    def test_start_progress_on_non_open_rejected(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        with self.assertRaises(ValidationError):
            bug_service.start_progress(bug_id)

    def test_start_progress_nonexistent_bug_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.start_progress(9999)

    # ---- mark_fixed ----

    def test_mark_fixed_success(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        bug_service.mark_fixed(bug_id, "Off-by-one in capacity comparison.",
                                "Changed >= to > in the check.", "test_allocation.py::test_room_at_capacity_rejected")
        bugs = bug_service.get_all_bugs()
        self.assertEqual(bugs[0]["status"], "Fixed")
        self.assertTrue(bugs[0]["root_cause"])

    def test_mark_fixed_before_in_progress_rejected(self):
        bug_id = self._log_sample_bug()
        with self.assertRaises(ValidationError):
            bug_service.mark_fixed(bug_id, "Some root cause here.", "Some fix here.", "test_x")

    def test_mark_fixed_empty_root_cause_rejected(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        with self.assertRaises(ValidationError):
            bug_service.mark_fixed(bug_id, "", "Some fix here.", "test_x")

    def test_mark_fixed_empty_test_case_rejected(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        with self.assertRaises(ValidationError):
            bug_service.mark_fixed(bug_id, "Root cause here.", "Fix here.", "")

    # ---- close_bug ----

    def test_close_bug_success(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        bug_service.mark_fixed(bug_id, "Root cause here.", "Fix applied.", "test_x")
        bug_service.close_bug(bug_id)
        bugs = bug_service.get_all_bugs()
        self.assertEqual(bugs[0]["status"], "Closed")

    def test_close_bug_before_fixed_rejected(self):
        bug_id = self._log_sample_bug()
        with self.assertRaises(ValidationError):
            bug_service.close_bug(bug_id)

    def test_close_already_closed_bug_rejected(self):
        bug_id = self._log_sample_bug()
        bug_service.start_progress(bug_id)
        bug_service.mark_fixed(bug_id, "Root cause here.", "Fix applied.", "test_x")
        bug_service.close_bug(bug_id)
        with self.assertRaises(ValidationError):
            bug_service.close_bug(bug_id)

    def test_close_nonexistent_bug_rejected(self):
        with self.assertRaises(ValidationError):
            bug_service.close_bug(9999)


if __name__ == "__main__":
    unittest.main()
