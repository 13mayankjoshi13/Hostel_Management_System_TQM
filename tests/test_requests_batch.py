"""Module Tests — signup approval, student edit/sort, bug reporter/fixer, people summary."""
import os
import sqlite3
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import (auth_service, student_service, bug_service, quality_service,
                           student_portal_service as portal)
from app.utils import session
from app.utils.validation import ValidationError


class Base(unittest.TestCase):

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
        session.clear_session()

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV, ls.DEFECT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)


class TestSignup(Base):

    def setUp(self):
        super().setUp()
        self.sid = student_service.add_student("Mayank Joshi", "2410302037", "9876543210")

    def _signup(self, **kw):
        args = dict(username="mayank", password="Secret123", registration_number="2410302037",
                    contact_number="9876543210")
        args.update(kw)
        return auth_service.register_student(**args)

    def test_signup_creates_pending_student_account(self):
        self._signup()
        user = auth_service.list_users()[0]
        self.assertEqual((user["role"], user["status"], user["student_id"]), ("Student", "Pending", self.sid))

    def test_pending_account_cannot_log_in_until_approved(self):
        user_id = self._signup()
        with self.assertRaisesRegex(ValidationError, "approve"):
            auth_service.authenticate("mayank", "Secret123")
        session.set_session("admin", "Administrator")
        auth_service.approve_user(user_id)
        session.clear_session()
        self.assertEqual(auth_service.authenticate("mayank", "Secret123")["student_id"], self.sid)

    def test_wrong_password_on_pending_account_gives_generic_error(self):
        self._signup()
        with self.assertRaisesRegex(ValidationError, "Invalid username or password"):
            auth_service.authenticate("mayank", "Wrong123")

    def test_unknown_registration_or_wrong_contact_rejected(self):
        with self.assertRaises(ValidationError):
            self._signup(registration_number="2410302099")
        with self.assertRaises(ValidationError):
            self._signup(contact_number="9876500000")

    def test_duplicate_username_and_second_account_rejected(self):
        self._signup()
        other = student_service.add_student("Test Student", "2410302099", "9876543211")
        with self.assertRaises(ValidationError):
            self._signup(username="MAYANK", registration_number="2410302099", contact_number="9876543211")
        with self.assertRaises(ValidationError):
            self._signup(username="another")
        self.assertIsNotNone(other)

    def test_invalid_signup_input_rejected(self):
        for kw in ({"username": "ab"}, {"password": "123"}, {"registration_number": "xx"}, {"contact_number": "12"}):
            with self.assertRaises(ValidationError, msg=str(kw)):
                self._signup(**kw)

    def test_only_administrator_can_approve(self):
        user_id = self._signup()
        for role in ("Warden", "Staff", "Student"):
            session.set_session("u", role, self.sid if role == "Student" else None)
            with self.assertRaises(ValidationError):
                auth_service.approve_user(user_id)

    def test_approve_errors(self):
        session.set_session("admin", "Administrator")
        with self.assertRaises(ValidationError):
            auth_service.approve_user(999)
        user_id = self._signup()
        auth_service.approve_user(user_id)
        with self.assertRaises(ValidationError):
            auth_service.approve_user(user_id)

    def test_admin_created_accounts_are_active_and_old_databases_migrate(self):
        user_id = auth_service.create_user("warden1", "Secret123", "Warden")
        self.assertEqual(next(u for u in auth_service.list_users() if u["user_id"] == user_id)["status"], "Active")
        old = os.path.join(self.tmp, "old.db")
        conn = sqlite3.connect(old)
        conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, role TEXT)")
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('a', 'x', 'Staff')")
        conn.execute("CREATE TABLE bugs (bug_id INTEGER PRIMARY KEY, title TEXT)")
        conn.commit()
        conn.close()
        initialize_database(old)
        conn = sqlite3.connect(old)
        self.assertEqual(conn.execute("SELECT status FROM users").fetchone()[0], "Active")
        self.assertIn("reported_by", {r[1] for r in conn.execute("PRAGMA table_info(bugs)")})
        conn.close()


class TestStudentEditAndSort(Base):

    def setUp(self):
        super().setUp()
        self.a = student_service.add_student("charlie Brown", "2410302003", "9876543210")
        self.b = student_service.add_student("Alice Smith", "2410302002", "9876543211")
        self.c = student_service.add_student("bob Stone", "2410302001", "9876543212")

    def _names(self, order):
        return [s["name"] for s in student_service.get_all_students(order)]

    def test_sort_options(self):
        self.assertEqual(self._names("Newest first"), ["bob Stone", "Alice Smith", "charlie Brown"])
        self.assertEqual(self._names("Oldest first"), ["charlie Brown", "Alice Smith", "bob Stone"])
        self.assertEqual(self._names("Name A-Z"), ["Alice Smith", "bob Stone", "charlie Brown"])
        self.assertEqual(self._names("Name Z-A"), ["charlie Brown", "bob Stone", "Alice Smith"])
        self.assertEqual(self._names("Registration No."), ["bob Stone", "Alice Smith", "charlie Brown"])

    def test_unknown_sort_falls_back_to_newest(self):
        self.assertEqual(self._names("nonsense"), self._names("Newest first"))

    def test_update_student(self):
        student_service.update_student(self.a, "Charlie Brown", "2410302003", "9123456789")
        row = next(s for s in student_service.get_all_students() if s["student_id"] == self.a)
        self.assertEqual((row["name"], row["contact_number"]), ("Charlie Brown", "9123456789"))

    def test_update_validates_and_rejects_duplicates_and_missing(self):
        with self.assertRaises(ValidationError):
            student_service.update_student(self.a, "Charlie Brown", "2410302002", "9876543210")
        with self.assertRaises(ValidationError):
            student_service.update_student(self.a, "Charlie Brown", "2410302003", "0123456789")
        with self.assertRaises(ValidationError):
            student_service.update_student(999, "Charlie Brown", "2410302003", "9876543210")

    def test_update_keeping_own_registration_number_is_allowed(self):
        student_service.update_student(self.a, "Charlie B", "2410302003", "9876543210")

    def test_student_role_cannot_use_admin_update(self):
        session.set_session("s", "Student", self.a)
        with self.assertRaises(ValidationError):
            student_service.update_student(self.b, "Hacked Name", "2410302002", "9876543211")


class TestPortalDetails(Base):

    def setUp(self):
        super().setUp()
        self.s1 = student_service.add_student("Mayank Joshi", "2410302037", "9876543210")
        self.s2 = student_service.add_student("Test Student", "2410302099", "9876543211")
        auth_service.create_user("student1", "Secret123", "Student", self.s1)

    def test_student_edits_own_name_and_contact_only(self):
        auth_service.authenticate("student1", "Secret123")
        portal.update_my_details("Mayank J", "9123456789")
        details = portal.my_details()
        self.assertEqual((details["name"], details["contact_number"], details["registration_number"]),
                         ("Mayank J", "9123456789", "2410302037"))
        other = next(s for s in student_service.get_all_students() if s["student_id"] == self.s2)
        self.assertEqual(other["name"], "Test Student")

    def test_invalid_own_details_rejected(self):
        auth_service.authenticate("student1", "Secret123")
        with self.assertRaises(ValidationError):
            portal.update_my_details("", "9123456789")
        with self.assertRaises(ValidationError):
            portal.update_my_details("Mayank J", "123")

    def test_non_student_session_rejected(self):
        session.set_session("admin", "Administrator")
        with self.assertRaises(ValidationError):
            portal.my_details()
        with self.assertRaises(ValidationError):
            portal.update_my_details("X Y", "9123456789")


class TestBugPeople(Base):

    def _bug(self, n, **kw):
        return bug_service.log_bug("Room", "Validation", f"Bug number {n}", "description text", "Low", "Low", **kw)

    def test_reporter_defaults_to_logged_in_user_and_can_be_set(self):
        session.set_session("admin", "Administrator")
        a = self._bug(1)
        b = self._bug(2, reported_by="Mayank")
        bugs = {x["bug_id"]: x for x in bug_service.get_all_bugs()}
        self.assertEqual((bugs[a]["reported_by"], bugs[b]["reported_by"]), ("admin", "Mayank"))

    def test_fixer_recorded_on_mark_fixed(self):
        session.set_session("admin", "Administrator")
        a = self._bug(1)
        bug_service.start_progress(a)
        bug_service.mark_fixed(a, "root cause x", "action taken", "test x", fixed_by="Mayank")
        bug = bug_service.get_all_bugs()[0]
        self.assertEqual((bug["status"], bug["fixed_by"]), ("Fixed", "Mayank"))

    def test_people_summary(self):
        a = self._bug(1, reported_by="Mayank")
        self._bug(2, reported_by="Mayank")
        self._bug(3, reported_by="Riya")
        bug_service.start_progress(a)
        bug_service.mark_fixed(a, "root cause x", "action taken", "test x", fixed_by="Mayank")
        self.assertEqual(quality_service.get_people_summary(), [("Mayank", 2, 1), ("Riya", 1, 0)])

    def test_people_summary_empty(self):
        self.assertEqual(quality_service.get_people_summary(), [])

    def test_log_bugs_loader_sets_mayank_and_backfills(self):
        from app.database import log_bugs
        conn = db_module.get_connection()
        conn.execute("INSERT INTO bugs (date, module, category, title, description, severity, priority, status) "
                     "VALUES ('2026-10-16', 'Room', 'Validation', 'Old bug without people', 'desc text', 'Low', 'Low', 'Fixed')")
        conn.commit()
        conn.close()
        log_bugs.run()
        bugs = bug_service.get_all_bugs()
        self.assertTrue(all(b["reported_by"] == "Mayank" for b in bugs))
        self.assertTrue(all(b["fixed_by"] == "Mayank" for b in bugs))


if __name__ == "__main__":
    unittest.main()
