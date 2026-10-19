import os
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, timedelta

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import allocation_service, auth_service, complaint_service, room_service, student_service
from app.utils import session
from app.utils.timefmt import local_iso_to_utc, utc_to_local
import app.utils.logging_service as ls


class TestTimestamps(unittest.TestCase):

    def setUp(self):
        self._tz = os.environ.get("TZ")
        os.environ["TZ"] = "Asia/Kolkata"
        time.tzset()
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.set_session("admin", "Administrator")

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()
        if self._tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = self._tz
        time.tzset()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _is_now(self, text):
        return abs(datetime.now() - datetime.strptime(text, "%Y-%m-%d %H:%M:%S")) < timedelta(minutes=2)

    def test_bug_039_utc_text_is_shown_in_local_time(self):
        self.assertEqual(utc_to_local("2026-10-19 04:22:33"), "2026-10-19 09:52:33")
        self.assertEqual(utc_to_local(None), None)
        self.assertEqual(utc_to_local("not a date"), "not a date")

    def test_bug_039_screens_get_local_times_for_new_records(self):
        sid = student_service.add_student("Kid A", "AB123", "9876500000")
        rid = room_service.add_room("A101", "Double", 2)
        allocation_service.allocate_room(sid, rid)
        cid = complaint_service.create_complaint(sid, "Maintenance", "Tap is leaking badly")
        complaint_service.resolve_complaint(cid, "Washer replaced")
        allocation = allocation_service.get_active_allocations()[0]
        complaint = complaint_service.get_all_complaints()[0]
        auth_service.create_user("boss", "Secret123", "Warden")
        for value in (allocation["allocated_at"], complaint["created_at"], complaint["resolved_at"],
                      auth_service.list_users()[0]["created_at"]):
            self.assertTrue(self._is_now(value), value)
        self.assertGreaterEqual(complaint["resolved_at"], complaint["created_at"])

    def test_bug_039_old_local_resolved_times_are_converted_once(self):
        sid = student_service.add_student("Kid A", "AB123", "9876500000")
        cid = complaint_service.create_complaint(sid, "Maintenance", "Tap is leaking badly")
        conn = sqlite3.connect(db_module.DATABASE_PATH)
        conn.execute("UPDATE complaints SET status = 'Resolved', resolved_at = '2026-10-19T09:52:33' "
                     "WHERE complaint_id = ?", (cid,))
        conn.commit()
        conn.close()
        initialize_database(db_module.DATABASE_PATH)
        initialize_database(db_module.DATABASE_PATH)
        conn = sqlite3.connect(db_module.DATABASE_PATH)
        stored = conn.execute("SELECT resolved_at FROM complaints").fetchone()[0]
        conn.close()
        self.assertEqual(stored, "2026-10-19 04:22:33")
        self.assertEqual(local_iso_to_utc("2026-10-19T09:52:33"), "2026-10-19 04:22:33")
        self.assertEqual(complaint_service.get_all_complaints()[0]["resolved_at"], "2026-10-19 09:52:33")


if __name__ == "__main__":
    unittest.main()
