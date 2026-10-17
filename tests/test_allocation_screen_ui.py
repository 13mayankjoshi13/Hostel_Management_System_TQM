"""UI regression tests for the Allocation screen. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import student_service, room_service


class TestAllocationScreenUI(unittest.TestCase):

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
        self.s1 = student_service.add_student("Aa Bb", "2410302001", "9876543210")
        self.s2 = student_service.add_student("Cc Dd", "2410302002", "9876543211")
        room_service.add_room("A1", "Single", 1)
        room_service.add_room("A2", "Double", 2)
        from app.theme import apply_theme, get_fonts
        from app.screens.allocation_screen import AllocationScreen

        apply_theme(self.root)
        self.screen = AllocationScreen(self.root, get_fonts())
        self.screen.refresh()
        from tkinter import messagebox
        self._boxes = (messagebox.showinfo, messagebox.showerror)
        messagebox.showinfo = messagebox.showerror = lambda *a, **k: None

    def tearDown(self):
        if not hasattr(self, "screen"):
            return
        from tkinter import messagebox
        messagebox.showinfo, messagebox.showerror = self._boxes
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _pick(self, student_part, room_part):
        screen = self.screen
        screen.student_var.set(next(k for k in screen._student_options if student_part in k))
        screen.room_var.set(next(k for k in screen._room_options if room_part in k))
        screen.on_allocate()

    def test_bug_013_allocated_student_and_full_room_leave_the_lists(self):
        self._pick("Aa Bb", "A1")
        self.assertFalse(any("Aa Bb" in k for k in self.screen._student_options))
        self.assertFalse(any("A1" in k for k in self.screen._room_options))
        self.assertTrue(any("Cc Dd" in k for k in self.screen._student_options))

    def test_bug_013_partly_full_room_stays_with_usage_shown(self):
        self._pick("Aa Bb", "A2")
        labels = [k for k in self.screen._room_options if "A2" in k]
        self.assertEqual(len(labels), 1)
        self.assertIn("1/2 used", labels[0])

    def test_bug_013_release_returns_student_and_room_to_the_lists(self):
        self._pick("Aa Bb", "A1")
        self.screen.tree.selection_set(self.screen.tree.get_children()[0])
        self.screen.on_release()
        self.assertTrue(any("Aa Bb" in k for k in self.screen._student_options))
        self.assertTrue(any("A1" in k for k in self.screen._room_options))


if __name__ == "__main__":
    unittest.main()
