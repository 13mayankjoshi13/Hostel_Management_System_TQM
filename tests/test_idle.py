import os
import tempfile
import tkinter as tk
import unittest
from unittest import mock

from app.utils.idle import IdleTracker


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class TestIdleTracker(unittest.TestCase):

    def test_bug_033_expires_after_timeout_and_activity_resets_it(self):
        clock = FakeClock()
        tracker = IdleTracker(60, clock=clock)
        clock.now += 59
        self.assertFalse(tracker.expired())
        tracker.touch()
        clock.now += 59
        self.assertFalse(tracker.expired())
        clock.now += 1
        self.assertTrue(tracker.expired())


class TestIdleLogoutUI(unittest.TestCase):

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
        from app.services import auth_service

        auth_service.create_user("boss", "Secret123", "Warden")
        from app.screens import main_window

        self.mw = main_window
        self.window = main_window.MainWindow(show_splash=False)
        for child in self.window.winfo_children():
            if child.winfo_class() == "Toplevel":
                child.destroy()
        self.auth = auth_service
        self.ready = True

    def tearDown(self):
        if not self.ready:
            return
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        from app.utils import session

        session.clear_session()
        self.window.destroy()
        config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_033_idle_session_is_logged_out_but_active_one_is_not(self):
        from app.utils import session

        self.auth.authenticate("boss", "Secret123")
        with mock.patch.object(self.mw.messagebox, "showinfo") as shown:
            self.window._check_idle()
            self.assertTrue(session.is_logged_in())
            self.assertFalse(shown.called)
            self.window._idle._last -= self.mw.IDLE_TIMEOUT_MINUTES * 60 + 1
            self.window._check_idle()
        self.assertFalse(session.is_logged_in())
        self.assertTrue(shown.called)


if __name__ == "__main__":
    unittest.main()
