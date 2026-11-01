"""Summary strips: correct numbers per role, and every screen still opens. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest


class TestPageStats(unittest.TestCase):

    def setUp(self):
        self.ready = False
        try:
            tk.Tk().destroy()
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
        from app.services import (allocation_service, fine_service, notice_service, room_service, student_service)

        self.s1 = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        student_service.add_student("Arjun Rao", "AB1001", "9876543201")
        room = room_service.add_room("G101", "Double", 2, 0, "Girls")
        allocation_service.allocate_room(self.s1, room)
        fine_service.issue_fine(self.s1, 250, "Late return")
        notice_service.send_notice("Water cut", "No water at noon", "All")
        from app.screens.main_window import MainWindow

        self.window = MainWindow(show_splash=False)
        for child in self.window.winfo_children():
            if child.winfo_class() == "Toplevel":
                child.destroy()
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

    def _log_in(self, username, role, student_id=None):
        from app.utils import session

        session.set_session(username, role, student_id)
        self.window._user = {"username": username, "role": role}
        self.window._enter_user_ui(self.window._user)

    def _values(self, key):
        strip = self.window.screens[key].stat_strip
        out = {}
        for card in strip.winfo_children():
            labels = [w.cget("text") for frame in card.body.winfo_children() if isinstance(frame, tk.Frame)
                      for w in frame.winfo_children() if isinstance(w, tk.Label)]
            out[labels[1]] = labels[0]
        return out

    def test_admin_screens_open_and_numbers_match_the_data(self):
        from app.screens.main_window import _allowed_screens

        self._log_in("boss", "Administrator")
        for key in _allowed_screens("Administrator"):
            self.window.show_screen(key)
            self.window.update()
        students = self._values("Students")
        self.assertEqual((students["Students"], students["With a room"], students["Without a room"],
                          students["Gender not set"]), ("2", "1", "1", "1"))
        self.assertEqual(self._values("Rooms")["Beds"], "2")
        self.assertEqual(self._values("Fines")["Unpaid fines"], "1")
        self.assertEqual(self._values("Notices")["Notices sent"], "1")
        self.assertEqual(self._values("Allocation")["Beds free"], "1")

    def test_student_screens_show_only_their_own_numbers(self):
        from app.screens.main_window import _allowed_screens

        self._log_in("meera", "Student", self.s1)
        for key in _allowed_screens("Student"):
            self.window.show_screen(key)
            self.window.update()
        self.assertEqual(self._values("MyFines")["Total"], "1")
        self.assertEqual(self._values("MyNotices")["Notices for you"], "1")

    def test_a_failing_provider_hides_the_strip_instead_of_breaking_the_screen(self):
        from unittest import mock
        from app.screens import page_stats

        self._log_in("boss", "Administrator")
        with mock.patch.dict(page_stats.PROVIDERS, {"Students": mock.Mock(side_effect=RuntimeError("boom"))}):
            self.window.screens["Students"].stat_strip._provider = page_stats.PROVIDERS["Students"]
            self.window.show_screen("Students")
        self.assertEqual(self.window.screens["Students"].stat_strip.winfo_children(), [])


if __name__ == "__main__":
    unittest.main()
