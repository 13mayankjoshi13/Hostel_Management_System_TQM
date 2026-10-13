"""Module Tests (Q09 feature #3) — holiday / event calendar."""
import os
import sqlite3
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import event_service
from app.utils import session
from app.utils.validation import ValidationError


class TestEvents(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        import app.config as config
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        ls.ERROR_LOG_CSV = os.path.join(self.tmp_dir, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp_dir, "a.csv")
        initialize_database(self.tmp_db)
        session.set_session("admin", "Administrator")

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()
        for name in os.listdir(self.tmp_dir):
            os.remove(os.path.join(self.tmp_dir, name))
        os.rmdir(self.tmp_dir)

    def test_add_and_list(self):
        event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event")
        events = event_service.get_all_events()
        self.assertEqual((events[0]["title"], events[0]["kind"]), ("Hostel Day", "Hostel Event"))

    def test_warden_allowed(self):
        session.set_session("w", "Warden")
        self.assertTrue(event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event"))

    def test_student_and_staff_rejected(self):
        for role in ("Student", "Staff"):
            session.set_session("u", role, 1 if role == "Student" else None)
            with self.assertRaises(ValidationError):
                event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event")

    def test_student_cannot_delete(self):
        event_id = event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event")
        session.set_session("s", "Student", 1)
        with self.assertRaises(ValidationError):
            event_service.delete_event(event_id)

    def test_duplicate_rejected(self):
        event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event")
        with self.assertRaises(ValidationError):
            event_service.add_event("2026-11-20", "Hostel Day", "Exam")

    def test_invalid_inputs_rejected(self):
        for args in (("20-11-2026", "Hostel Day", "Holiday"), ("2026-02-30", "Hostel Day", "Holiday"),
                     ("2026-11-20", "ab", "Holiday"), ("2026-11-20", "x" * 61, "Holiday"),
                     ("2026-11-20", "Hostel Day", "Party")):
            with self.assertRaises(ValidationError, msg=str(args)):
                event_service.add_event(*args)

    def test_delete(self):
        event_id = event_service.add_event("2026-11-20", "Hostel Day", "Hostel Event")
        event_service.delete_event(event_id)
        self.assertEqual(event_service.get_all_events(), [])
        with self.assertRaises(ValidationError):
            event_service.delete_event(event_id)

    def test_month_and_upcoming(self):
        event_service.add_event("2026-11-20", "A event", "Exam")
        event_service.add_event("2026-12-05", "B event", "Exam")
        self.assertEqual([e["title"] for e in event_service.get_events_for_month(2026, 11)], ["A event"])
        self.assertEqual([e["title"] for e in event_service.get_upcoming("2026-11-21", 5)], ["B event"])

    def test_default_holidays_idempotent(self):
        event_service.ensure_default_holidays()
        count = len(event_service.get_all_events())
        self.assertEqual(count, len(event_service.DEFAULT_HOLIDAYS))
        event_service.ensure_default_holidays()
        self.assertEqual(len(event_service.get_all_events()), count)

    def test_events_table_added_to_existing_database(self):
        old = os.path.join(self.tmp_dir, "old.db")
        conn = sqlite3.connect(old)
        conn.execute("CREATE TABLE students (student_id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        initialize_database(old)
        conn = sqlite3.connect(old)
        names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        conn.close()
        self.assertIn("events", names)


if __name__ == "__main__":
    unittest.main()
