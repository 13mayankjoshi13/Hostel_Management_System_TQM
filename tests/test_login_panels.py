import os
import tempfile
import tkinter as tk
import unittest

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import auth_service, student_service
from app.utils import session
from app.utils.validation import ValidationError


class TestLoginPanels(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        sid = student_service.add_student("Kid One", "AB1234", "9876543210")
        auth_service.create_user("boss", "Secret123", "Administrator")
        auth_service.create_user("warden1", "Secret123", "Warden")
        auth_service.create_user("staff1", "Secret123", "Staff")
        auth_service.create_user("kid1", "Secret123", "Student", sid)
        session.clear_session()

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_each_account_signs_in_only_on_its_own_panel(self):
        allowed = {"boss": "Administrator", "warden1": "Staff", "staff1": "Staff", "kid1": "Student"}
        for username, own in allowed.items():
            for panel in auth_service.LOGIN_PANELS:
                session.clear_session()
                if panel == own:
                    self.assertEqual(auth_service.authenticate(username, "Secret123", panel)["username"], username)
                else:
                    with self.assertRaises(ValidationError) as ctx:
                        auth_service.authenticate(username, "Secret123", panel)
                    self.assertIn(own, str(ctx.exception))
                    self.assertFalse(session.is_logged_in())

    def test_wrong_panel_with_wrong_password_reveals_nothing_and_unknown_panel_is_refused(self):
        with self.assertRaises(ValidationError) as ctx:
            auth_service.authenticate("boss", "wrong-password", "Student")
        self.assertEqual(str(ctx.exception), auth_service.LOGIN_FAILED_MESSAGE)
        with self.assertRaises(ValidationError):
            auth_service.authenticate("boss", "Secret123", "Hacker")
        self.assertEqual(auth_service.authenticate("boss", "Secret123")["role"], "Administrator")

    def test_login_screen_tabs_pass_the_selected_panel(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        root.withdraw()
        try:
            from app.screens.login_screen import LoginScreen
            from app.theme import apply_theme, get_fonts

            apply_theme(root)
            got = []
            screen = LoginScreen(root, get_fonts(), on_success=got.append)
            self.assertEqual(screen.panel, "Student")
            self.assertTrue(screen.signup_label.winfo_manager())
            screen.select_panel("Administrator")
            self.assertFalse(screen.signup_label.winfo_manager())
            self.assertTrue(screen.hint_label.winfo_manager())
            screen.username_var.set("boss")
            screen.password_var.set("Secret123")
            screen.select_panel("Staff")
            screen.username_var.set("boss")
            screen.password_var.set("Secret123")
            screen.on_login()
            self.assertEqual(got, [])
            self.assertIn("Administrator", screen.error_label.cget("text"))
            screen.select_panel("Administrator")
            screen.username_var.set("boss")
            screen.password_var.set("Secret123")
            screen.on_login()
            self.assertEqual(got[0]["role"], "Administrator")
        finally:
            session.clear_session()
            root.destroy()


if __name__ == "__main__":
    unittest.main()
