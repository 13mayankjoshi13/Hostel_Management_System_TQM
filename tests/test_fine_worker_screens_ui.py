"""Fines, My Fines and Workers screens build, refresh and show data. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest


class TestNewScreens(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.root.withdraw()
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        db_module.initialize_database(config.DATABASE_PATH)
        from app.utils import session

        session.clear_session()

    def tearDown(self):
        if not hasattr(self, "tmp"):
            return
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        from app.utils import session

        session.clear_session()
        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.root.destroy()

    def test_screens_show_rows_and_the_main_window_routes_them_by_role(self):
        from app.screens.fine_screen import FineScreen
        from app.screens.main_window import _allowed_screens
        from app.screens.my_fines_screen import MyFinesScreen
        from app.screens.worker_screen import WorkerScreen
        from app.services import fine_service, student_service, worker_service
        from app.theme import apply_theme, get_fonts
        from app.utils import session

        apply_theme(self.root)
        sid = student_service.add_student("Ravi Kumar", "AB1234", "9876543210")
        fine_service.issue_fine(sid, "250", "Late return after curfew")
        worker_service.add_worker("Ramesh Yadav", "Electrician", "9876543210")
        fines, workers = FineScreen(self.root, get_fonts()), WorkerScreen(self.root, get_fonts())
        self.assertEqual(len(fines.tree.get_children()), 1)
        self.assertEqual(len(workers.tree.get_children()), 1)
        session.set_session("ravi", "Student", sid)
        mine = MyFinesScreen(self.root, get_fonts())
        mine.refresh()
        self.assertEqual(len(mine.tree.get_children()), 1)
        self.assertIn("MyFines", _allowed_screens("Student"))
        self.assertNotIn("Fines", _allowed_screens("Student"))
        self.assertNotIn("Workers", _allowed_screens("Student"))
        for role in ("Administrator", "Warden", "Staff"):
            self.assertIn("Fines", _allowed_screens(role))
            self.assertIn("Workers", _allowed_screens(role))
            self.assertNotIn("MyFines", _allowed_screens(role))


if __name__ == "__main__":
    unittest.main()
