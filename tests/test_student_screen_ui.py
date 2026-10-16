"""UI regression tests for the Students screen. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service


class TestStudentScreenUI(unittest.TestCase):

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
        student_service.add_student("Charlie Brown", "2410302003", "9876543210")
        student_service.add_student("Alice Smith", "2410302002", "9876543211")
        from app.theme import apply_theme, get_fonts
        from app.screens.student_screen import StudentScreen

        apply_theme(self.root)
        self.screen = StudentScreen(self.root, get_fonts())

    def tearDown(self):
        if not hasattr(self, "screen"):
            return
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_012_selection_kept_after_resort(self):
        screen = self.screen
        screen.tree.selection_set(screen.tree.get_children()[0])
        self.root.update()
        edited = screen._editing_id
        screen.sort_var.set("Name Z-A")
        screen.refresh()
        selected = screen.tree.selection()
        self.assertEqual(len(selected), 1)
        self.assertEqual(int(screen.tree.item(selected[0], "values")[0]), edited)

    def test_bug_012_unsaved_typing_survives_refresh(self):
        screen = self.screen
        screen.tree.selection_set(screen.tree.get_children()[0])
        self.root.update()
        screen.name_var.set("Typed Not Saved")
        screen.refresh()
        self.assertEqual(screen.name_var.get(), "Typed Not Saved")

    def test_bug_012_edit_state_cleared_if_student_vanishes(self):
        screen = self.screen
        screen.tree.selection_set(screen.tree.get_children()[0])
        self.root.update()
        student_service.delete_student(screen._editing_id)
        screen.refresh()
        self.assertIsNone(screen._editing_id)


if __name__ == "__main__":
    unittest.main()
