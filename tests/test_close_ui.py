"""The application can be closed from the log-in window and logs the user out when closed. Needs a display."""
import os
import tempfile
import tkinter as tk
import unittest


class TestClose(unittest.TestCase):

    def setUp(self):
        self.ready = False
        try:
            probe = tk.Tk()
            probe.destroy()
        except tk.TclError:
            self.skipTest("no display available")
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        db_module.initialize_database(config.DATABASE_PATH)
        self.ls = ls
        self.ready = True

    def tearDown(self):
        if not self.ready:
            return
        import app.config as config
        import app.database.db as db_module
        from app.utils import session

        session.clear_session()
        config.DATABASE_PATH, db_module.DATABASE_PATH, self.ls.ERROR_LOG_CSV, self.ls.AUDIT_LOG_CSV = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _window(self):
        from app.screens.main_window import MainWindow

        return MainWindow(show_splash=False)

    def test_bug_040_closing_the_login_window_quits_the_application(self):
        window = self._window()
        login = next(c for c in window.winfo_children() if c.winfo_class() == "Toplevel")
        login.on_close_request()
        with self.assertRaises(tk.TclError):
            window.title()

    def test_bug_040_closing_the_main_window_logs_the_user_out(self):
        from app.services import auth_service
        from app.utils import session

        auth_service.create_user("boss", "Secret123", "Warden")
        window = self._window()
        auth_service.authenticate("boss", "Secret123")
        window.exit_app()
        self.assertFalse(session.is_logged_in())
        with open(self.ls.AUDIT_LOG_CSV, encoding="utf-8") as f:
            self.assertIn("Logout", f.read())


if __name__ == "__main__":
    unittest.main()
