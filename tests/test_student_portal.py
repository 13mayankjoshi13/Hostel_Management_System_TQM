"""Module Tests (Q09 feature #3) — Student role and self-service portal."""
import os
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import (auth_service, student_service, room_service, allocation_service,
                           student_portal_service as portal)
from app.utils import session
from app.utils.validation import ValidationError


def _day(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


class TestStudentPortal(unittest.TestCase):

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
        session.clear_session()

        self.s1 = student_service.add_student("Mayank Joshi", "2410302037", "9876543210")
        self.s2 = student_service.add_student("Test Student", "2410302099", "9876543211")
        self.room1 = room_service.add_room("A101", "Single", 1)
        self.room2 = room_service.add_room("A102", "Single", 1)
        allocation_service.allocate_room(self.s1, self.room1)
        allocation_service.allocate_room(self.s2, self.room2)
        auth_service.create_user("student1", "Secret123", "Student", self.s1)
        auth_service.create_user("student2", "Secret123", "Student", self.s2)

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()
        for name in os.listdir(self.tmp_dir):
            os.remove(os.path.join(self.tmp_dir, name))
        os.rmdir(self.tmp_dir)

    def _login(self, username):
        auth_service.authenticate(username, "Secret123")

    # ---- accounts ----

    def test_student_account_requires_student_link(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("student3", "Secret123", "Student")

    def test_non_student_account_cannot_have_link(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("warden1", "Secret123", "Warden", self.s1)

    def test_student_cannot_have_two_accounts(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("student3", "Secret123", "Student", self.s1)

    def test_student_account_unknown_student_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("student3", "Secret123", "Student", 999)

    def test_login_sets_student_id_in_session(self):
        result = auth_service.authenticate("student1", "Secret123")
        self.assertEqual(result["student_id"], self.s1)
        self.assertEqual(session.get_student_id(), self.s1)

    def test_logout_clears_student_id(self):
        self._login("student1")
        auth_service.logout()
        self.assertIsNone(session.get_student_id())

    def test_list_users_shows_linked_student_name(self):
        names = {u["username"]: u["student_name"] for u in auth_service.list_users()}
        self.assertEqual(names["student1"], "Mayank Joshi")

    # ---- portal ----

    def test_my_room_returns_own_room(self):
        self._login("student1")
        self.assertEqual(portal.my_room()["room_number"], "A101")

    def test_my_room_none_when_not_allocated(self):
        s3 = student_service.add_student("No Room", "2410302100", "9876543212")
        auth_service.create_user("student3", "Secret123", "Student", s3)
        self._login("student3")
        self.assertIsNone(portal.my_room())

    def test_file_complaint_belongs_to_student_and_is_open(self):
        self._login("student1")
        portal.file_complaint("Food", "Food quality is poor.")
        mine = portal.my_complaints()
        self.assertEqual((len(mine), mine[0]["status"], mine[0]["category"]), (1, "Open", "Food"))

    def test_students_only_see_their_own_complaints(self):
        self._login("student1")
        portal.file_complaint("Washroom", "Tap is leaking badly.")
        self._login("student2")
        self.assertEqual(portal.my_complaints(), [])

    def test_invalid_complaint_rejected(self):
        self._login("student1")
        with self.assertRaises(ValidationError):
            portal.file_complaint("Food", "bad")

    def test_apply_leave_and_return(self):
        self._login("student1")
        leave_id = portal.apply_leave(_day(-9), _day(-5), "Family function")
        self.assertEqual(portal.my_leaves()[0]["status"], "On Leave")
        portal.return_from_leave(leave_id)
        self.assertEqual(portal.my_leaves()[0]["status"], "Returned")

    def test_student_cannot_return_another_students_leave(self):
        self._login("student1")
        leave_id = portal.apply_leave(_day(-9), _day(-5), "Family function")
        self._login("student2")
        with self.assertRaises(ValidationError):
            portal.return_from_leave(leave_id)
        self.assertEqual(portal.my_leaves(), [])

    def test_students_only_see_their_own_leaves(self):
        self._login("student1")
        portal.apply_leave(_day(-9), _day(-5), "Family function")
        self._login("student2")
        self.assertEqual(portal.my_leaves(), [])

    def test_portal_rejects_non_student_session(self):
        auth_service.create_user("warden1", "Secret123", "Warden")
        self._login("warden1")
        with self.assertRaises(ValidationError):
            portal.my_complaints()

    def test_portal_rejects_logged_out_session(self):
        with self.assertRaises(ValidationError):
            portal.my_room()


class TestUsersMigration(unittest.TestCase):

    def test_existing_database_gets_student_id_column(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "old.db")
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, "
                     "password_hash TEXT NOT NULL, role TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')))")
        conn.commit()
        conn.close()
        initialize_database(path)
        conn = sqlite3.connect(path)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
        conn.close()
        os.remove(path)
        os.rmdir(tmp)
        self.assertIn("student_id", columns)


if __name__ == "__main__":
    unittest.main()
