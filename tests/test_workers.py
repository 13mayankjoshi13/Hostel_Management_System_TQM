import os
import tempfile
import unittest
from datetime import date, timedelta

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import complaint_service, student_service, worker_service
from app.utils import session
from app.utils.validation import ValidationError


class TestWorkers(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_add_validates_and_rejects_duplicates_and_students(self):
        worker_service.add_worker("Ramesh Yadav", "Electrician", "+91 98765 43210")
        worker_service.add_worker("रमेश यादव", "Cleaner", "9876543211")
        for args in (("R", "Cleaner", "9876543210"), ("Ramesh Yadav", "Pilot", "9876543210"),
                     ("Ramesh Yadav", "Cleaner", "12345"), ("Ramesh Yadav", "Electrician", "9876543210"),
                     ("=cmd", "Cleaner", "9876543210")):
            with self.assertRaises(ValidationError):
                worker_service.add_worker(*args)
        student = student_service.add_student("Kid One", "AB1234", "9876543299")
        session.set_session("kid", "Student", student)
        with self.assertRaises(ValidationError):
            worker_service.add_worker("Sam Peter", "Cleaner", "9876543212")
        with self.assertRaises(ValidationError):
            worker_service.get_workers()

    def test_attendance_is_one_per_day_limited_in_time_and_active_only(self):
        wid = worker_service.add_worker("Ramesh Yadav", "Electrician", "9876543210")
        worker_service.mark_attendance(wid, "Present")
        worker_service.mark_attendance(wid, "Absent")
        self.assertEqual(worker_service.get_workers()[0]["today"], "Absent")
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        worker_service.mark_attendance(wid, "Present", yesterday)
        for status, day in (("Late", None), ("Present", (date.today() + timedelta(days=1)).isoformat()),
                            ("Present", (date.today() - timedelta(days=30)).isoformat()), ("Present", "tomorrow")):
            with self.assertRaises(ValidationError):
                worker_service.mark_attendance(wid, status, day)
        with self.assertRaises(ValidationError):
            worker_service.mark_attendance(999, "Present")
        worker_service.set_worker_active(wid, False)
        with self.assertRaises(ValidationError):
            worker_service.mark_attendance(wid, "Present")
        self.assertEqual(worker_service.get_workers(active_only=True), [])
        self.assertEqual(len(worker_service.get_workers()), 1)

    def test_workload_counts_assigned_and_resolved_complaints(self):
        worker_service.add_worker("रमेश यादव", "Plumber", "9876543210")
        student = student_service.add_student("Kid One", "AB1234", "9876543299")
        c1 = complaint_service.create_complaint(student, "Maintenance", "Tap is leaking badly")
        c2 = complaint_service.create_complaint(student, "Maintenance", "Another tap is leaking")
        for c in (c1, c2):
            complaint_service.assign_complaint(c, "रमेश यादव")
        complaint_service.resolve_complaint(c2, "Replaced washer")
        row = worker_service.get_workers()[0]
        self.assertEqual((row["open_jobs"], row["done_jobs"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
