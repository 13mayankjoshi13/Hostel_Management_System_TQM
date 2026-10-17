"""UI regression tests: the selected row survives a refresh. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest
from tkinter import messagebox, simpledialog

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, room_service, allocation_service, complaint_service, bug_service


class TestSelectionKept(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.root.withdraw()
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV, ls.DEFECT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        ls.DEFECT_LOG_CSV = os.path.join(self.tmp, "d.csv")
        initialize_database(config.DATABASE_PATH)
        self._dialogs = (messagebox.showinfo, messagebox.showerror, simpledialog.askstring)
        messagebox.showinfo = messagebox.showerror = lambda *a, **k: None
        simpledialog.askstring = lambda *a, **k: "Hostel Maintenance"
        from app.theme import apply_theme, get_fonts

        apply_theme(self.root)
        self.fonts = get_fonts()
        self.ready = True

    def tearDown(self):
        if not getattr(self, "ready", False):
            return
        messagebox.showinfo, messagebox.showerror, simpledialog.askstring = self._dialogs
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV, ls.DEFECT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _select_first(self, screen):
        screen.tree.selection_set(screen.tree.get_children()[0])
        self.root.update()

    def test_bug_014_complaint_stays_selected_after_assign(self):
        from app.screens.complaint_screen import ComplaintScreen

        sid = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        complaint_service.create_complaint(sid, "Food", "The food was cold today")
        screen = ComplaintScreen(self.root, self.fonts)
        screen.refresh()
        self._select_first(screen)
        screen.on_assign()
        self.assertEqual(len(screen.tree.selection()), 1)
        screen.on_resolve()
        self.assertEqual(complaint_service.get_all_complaints()[0]["status"], "Resolved")

    def test_bug_014_leave_stays_selected_after_refresh(self):
        from app.screens.leave_screen import LeaveScreen
        from app.services import leave_service

        sid = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        allocation_service.allocate_room(sid, room_service.add_room("A1", "Single", 1))
        leave_service.record_leave(sid, __import__("datetime").date.today().isoformat(),
                                   __import__("datetime").date.today().isoformat(), "Home visit")
        screen = LeaveScreen(self.root, self.fonts)
        screen.refresh()
        self._select_first(screen)
        screen.refresh_table()
        self.assertEqual(len(screen.tree.selection()), 1)

    def test_bug_014_bug_stays_selected_and_detail_updates(self):
        from app.screens.bug_screen import BugScreen

        bug_service.log_bug("Room", "Validation", "Some test bug", "description text", "Low", "Low")
        screen = BugScreen(self.root, self.fonts)
        self._select_first(screen)
        screen.on_start_progress()
        self.root.update()
        self.assertEqual(len(screen.tree.selection()), 1)
        self.assertIn("Some test bug", screen.detail.cget("text"))

    def test_bug_014_selection_gone_row_does_not_error(self):
        from app.screens.bug_screen import BugScreen

        bug_service.log_bug("Room", "Validation", "Some test bug", "description text", "Low", "Low")
        screen = BugScreen(self.root, self.fonts)
        self._select_first(screen)
        screen.filter_var.set("Solved")
        screen.refresh()
        self.root.update()
        self.assertEqual(screen.tree.selection(), ())
        self.assertIn("Select a bug", screen.detail.cget("text"))


if __name__ == "__main__":
    unittest.main()
