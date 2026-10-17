"""UI regression tests for the sign-up dialog. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, auth_service


class TestSignupUI(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.root.withdraw()
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        student_service.add_student("Test Kid", "2410302099", "9876500000")
        from app.theme import apply_theme, get_fonts
        from app.screens.signup_screen import SignupDialog

        apply_theme(self.root)
        self.dialog = SignupDialog(self.root, get_fonts())
        self.ready = True

    def tearDown(self):
        if not getattr(self, "ready", False):
            return
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.dialog.destroy()
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _fill(self, **overrides):
        values = dict(reg="2410302099", contact="9876500000", username="testkid",
                      password="Secret123", confirm="Secret123")
        values.update(overrides)
        for key, value in values.items():
            self.dialog.vars[key].set(value)

    def test_mismatched_passwords_stop_before_the_service(self):
        self._fill(confirm="different")
        self.dialog.on_submit()
        self.assertIn("do not match", self.dialog.message.cget("text"))
        self.assertEqual(auth_service.list_users(), [])

    def test_wrong_contact_shows_error_and_allows_retry(self):
        self._fill(contact="9999999999")
        self.dialog.on_submit()
        self.assertIn("do not match a hostel record", self.dialog.message.cget("text"))
        self.assertFalse(self.dialog.submit_button.instate(["disabled"]))

    def test_bug_015_success_locks_the_form_and_keeps_the_message(self):
        self._fill()
        self.dialog.on_submit()
        self.assertTrue(self.dialog.submit_button.instate(["disabled"]))
        self.assertEqual(self.dialog.cancel_button.cget("text"), "Close")
        self.assertIn("Request sent", self.dialog.message.cget("text"))
        self.assertEqual(len(auth_service.list_users()), 1)


if __name__ == "__main__":
    unittest.main()
