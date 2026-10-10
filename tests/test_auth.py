"""
Module Tests (Q09 feature #3) — Authentication (Batch 9).

Covers password hashing round-trip, account creation/duplicate
rejection, login success/failure, logout, and the first-run default
admin bootstrap. Same temp-DB / temp-CSV isolation pattern as every
other test module.
"""
import os
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import auth_service
from app.utils import session
from app.utils.validation import ValidationError


class TestAuthentication(unittest.TestCase):

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
        auth_service.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv

        initialize_database(self.tmp_db)
        session.clear_session()

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as logging_service

        config.DATABASE_PATH = self._original_db_path
        db_module.DATABASE_PATH = self._original_db_path
        logging_service.ERROR_LOG_CSV = self._original_error_csv
        logging_service.AUDIT_LOG_CSV = self._original_audit_csv
        session.clear_session()

        for path in (self.tmp_db, self.tmp_error_csv, self.tmp_audit_csv):
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.tmp_dir)

    # ---- hashing ----

    def test_password_hash_roundtrip(self):
        hashed = auth_service._hash_password("Secret123")
        self.assertTrue(auth_service._verify_password("Secret123", hashed))

    def test_password_hash_wrong_password_fails(self):
        hashed = auth_service._hash_password("Secret123")
        self.assertFalse(auth_service._verify_password("WrongPass1", hashed))

    def test_password_hash_is_salted_differently_each_time(self):
        h1 = auth_service._hash_password("Secret123")
        h2 = auth_service._hash_password("Secret123")
        self.assertNotEqual(h1, h2)

    # ---- create_user ----

    def test_create_user_success(self):
        user_id = auth_service.create_user("warden1", "Passw0rd", "Warden")
        self.assertIsInstance(user_id, int)

    def test_create_user_duplicate_username_rejected(self):
        auth_service.create_user("warden1", "Passw0rd", "Warden")
        with self.assertRaises(ValidationError):
            auth_service.create_user("warden1", "Another1", "Staff")

    def test_create_user_short_password_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("staff1", "ab1", "Staff")

    def test_create_user_password_without_digit_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("staff1", "abcdefgh", "Staff")

    def test_create_user_invalid_role_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("staff1", "Passw0rd", "Manager")

    def test_create_user_invalid_username_characters_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.create_user("staff one!", "Passw0rd", "Staff")

    # ---- authenticate ----

    def test_authenticate_success_sets_session(self):
        auth_service.create_user("warden1", "Passw0rd", "Warden")
        result = auth_service.authenticate("warden1", "Passw0rd")
        self.assertEqual(result["username"], "warden1")
        self.assertEqual(result["role"], "Warden")
        self.assertTrue(session.is_logged_in())
        self.assertEqual(session.get_user(), "warden1")

    def test_authenticate_wrong_password_rejected(self):
        auth_service.create_user("warden1", "Passw0rd", "Warden")
        with self.assertRaises(ValidationError):
            auth_service.authenticate("warden1", "WrongPass1")

    def test_authenticate_nonexistent_user_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.authenticate("ghost", "Passw0rd")

    def test_authenticate_empty_fields_rejected(self):
        with self.assertRaises(ValidationError):
            auth_service.authenticate("", "")

    # ---- logout ----

    def test_logout_clears_session(self):
        auth_service.create_user("warden1", "Passw0rd", "Warden")
        auth_service.authenticate("warden1", "Passw0rd")
        auth_service.logout()
        self.assertFalse(session.is_logged_in())

    # ---- bootstrap ----

    def test_ensure_default_admin_creates_one_on_empty_table(self):
        auth_service.ensure_default_admin()
        result = auth_service.authenticate("admin", "admin123")
        self.assertEqual(result["role"], "Administrator")

    def test_ensure_default_admin_does_nothing_if_users_exist(self):
        auth_service.create_user("warden1", "Passw0rd", "Warden")
        auth_service.ensure_default_admin()
        with self.assertRaises(ValidationError):
            auth_service.authenticate("admin", "admin123")

    # ---- user management ----

    def test_list_users_excludes_password_hash(self):
        auth_service.create_user("warden1", "Secret123", "Warden")
        users = auth_service.list_users()
        self.assertEqual(len(users), 1)
        self.assertNotIn("password_hash", users[0])

    def test_change_password_allows_new_login_and_blocks_old(self):
        uid = auth_service.create_user("warden1", "Secret123", "Warden")
        auth_service.change_password(uid, "Newpass456")
        auth_service.authenticate("warden1", "Newpass456")
        with self.assertRaises(ValidationError):
            auth_service.authenticate("warden1", "Secret123")

    def test_change_password_rejects_weak_password(self):
        uid = auth_service.create_user("warden1", "Secret123", "Warden")
        with self.assertRaises(ValidationError):
            auth_service.change_password(uid, "abc")

    def test_change_password_unknown_user(self):
        with self.assertRaises(ValidationError):
            auth_service.change_password(999, "Secret123")

    def test_delete_user_removes_account(self):
        auth_service.create_user("admin1", "Secret123", "Administrator")
        uid = auth_service.create_user("staff1", "Secret123", "Staff")
        auth_service.delete_user(uid)
        self.assertEqual([u["username"] for u in auth_service.list_users()], ["admin1"])

    def test_delete_own_account_blocked(self):
        uid = auth_service.create_user("admin1", "Secret123", "Administrator")
        auth_service.create_user("admin2", "Secret123", "Administrator")
        auth_service.authenticate("admin1", "Secret123")
        with self.assertRaises(ValidationError):
            auth_service.delete_user(uid)

    def test_delete_last_administrator_blocked(self):
        uid = auth_service.create_user("admin1", "Secret123", "Administrator")
        with self.assertRaises(ValidationError):
            auth_service.delete_user(uid)
        self.assertEqual(len(auth_service.list_users()), 1)

    def test_delete_unknown_user(self):
        with self.assertRaises(ValidationError):
            auth_service.delete_user(999)


if __name__ == "__main__":
    unittest.main()
