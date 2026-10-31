import os
import sqlite3
import tempfile
import unittest

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.screens.main_window import ROLE_SCREENS, _NAV_ITEMS, _allowed_screens
from app.services import (allocation_service, auth_service, bug_service, fine_service, room_service,
                          student_service, worker_service)
from app.utils import session
from app.utils.validation import ValidationError, validate_role


class TestRoles(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        self.sid = student_service.add_student("Kid One", "AB1234", "9876543210")
        self.room = room_service.add_room("A1", "Single", 1)

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def _blocked(self, role, call):
        session.set_session("someone", role, self.sid if role == "Student" else None)
        try:
            with self.assertRaises(ValidationError, msg=f"{role} should be blocked"):
                call()
        finally:
            session.clear_session()

    def _allowed(self, role, call):
        session.set_session("someone", role)
        try:
            return call()
        finally:
            session.clear_session()

    def test_role_names_are_validated_case_insensitively(self):
        self.assertEqual(validate_role("super   admin"), "Super Admin")
        self.assertEqual(validate_role("WARDEN"), "Warden")
        with self.assertRaises(ValidationError):
            validate_role("Root")

    def test_each_role_gets_its_own_features(self):
        sets = {r: set(_allowed_screens(r)) for r in ROLE_SCREENS}
        self.assertEqual(len({frozenset(s) for s in sets.values()}), 4)
        for key in ("Rooms", "Bugs", "Quality", "Users"):
            self.assertNotIn(key, sets["Warden"])
            self.assertNotIn(key, sets["Staff"])
            self.assertNotIn(key, sets["Student"])
        self.assertNotIn("Fines", sets["Staff"])
        self.assertNotIn("Students", sets["Staff"])
        self.assertTrue(all(k.startswith("My") or k == "Calendar" for k in sets["Student"]))
        self.assertEqual(sets["Administrator"], sets["Super Admin"])
        known = {k for k, _, _ in _NAV_ITEMS}
        for wanted in ROLE_SCREENS.values():
            self.assertTrue(set(wanted) <= known)

    def test_services_enforce_what_the_menus_hide(self):
        for role in ("Warden", "Staff", "Student"):
            self._blocked(role, lambda: room_service.add_room("B1", "Single", 1))
            self._blocked(role, lambda: bug_service.get_all_bugs())
            self._blocked(role, lambda: auth_service.list_users())
        self._blocked("Staff", lambda: student_service.add_student("Kid Two", "AB5678", "9876543211"))
        self._blocked("Staff", lambda: student_service.update_student(self.sid, "Kid One", "AB1234", "9876543210"))
        self._blocked("Staff", lambda: student_service.delete_student(self.sid))
        self._blocked("Staff", lambda: allocation_service.allocate_room(self.sid, self.room))
        self._blocked("Staff", lambda: fine_service.issue_fine(self.sid, "10", "Test reason"))
        self._blocked("Warden", lambda: worker_service.add_worker("Ram Das", "Cleaner", "9876543210"))
        self._allowed("Warden", lambda: allocation_service.allocate_room(self.sid, self.room))
        self._allowed("Warden", lambda: fine_service.issue_fine(self.sid, "10", "Test reason"))
        self._allowed("Administrator", lambda: room_service.add_room("B1", "Single", 1))
        wid = self._allowed("Administrator", lambda: worker_service.add_worker("Ram Das", "Cleaner", "9876543210"))
        self._allowed("Staff", lambda: worker_service.mark_attendance(wid, "Present"))

    def test_only_a_super_admin_manages_administrator_accounts(self):
        session.set_session("chief", "Super Admin")
        admin_id = auth_service.create_user("boss", "Secret123", "Administrator")
        super_id = auth_service.create_user("chief2", "Secret123", "Super Admin")
        warden_id = auth_service.create_user("warden1", "Secret123", "Warden")
        session.set_session("boss", "Administrator")
        auth_service.change_password(warden_id, "Newpass456")
        for call in (lambda: auth_service.create_user("boss2", "Secret123", "Administrator"),
                     lambda: auth_service.create_user("chief3", "Secret123", "Super Admin"),
                     lambda: auth_service.change_password(super_id, "Hacked12345"),
                     lambda: auth_service.delete_user(super_id)):
            with self.assertRaises(ValidationError):
                call()
        auth_service.create_user("staff1", "Secret123", "Staff")
        auth_service.delete_user(warden_id)
        session.set_session("chief", "Super Admin")
        auth_service.change_password(admin_id, "Newpass456")
        auth_service.delete_user(admin_id)

    def test_last_super_admin_cannot_be_deleted_and_default_admin_is_a_super_admin(self):
        auth_service.ensure_default_admin()
        self.assertEqual(auth_service.authenticate("admin", "admin123")["role"], "Super Admin")
        users = auth_service.list_users()
        with self.assertRaises(ValidationError):
            auth_service.delete_user(users[0]["user_id"])

    def test_existing_database_promotes_its_first_administrator_once(self):
        conn = sqlite3.connect(db_module.DATABASE_PATH)
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('old_admin', 'x', 'Administrator')")
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES ('second', 'x', 'Administrator')")
        conn.commit()
        conn.close()
        auth_service.ensure_default_admin()
        auth_service.ensure_default_admin()
        roles = {u["username"]: u["role"] for u in auth_service.list_users()}
        self.assertEqual(roles, {"old_admin": "Super Admin", "second": "Administrator"})


if __name__ == "__main__":
    unittest.main()
