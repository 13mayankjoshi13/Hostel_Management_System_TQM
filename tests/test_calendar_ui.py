"""UI regression tests for the calendar screen. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest
from datetime import date
from unittest import mock

from app.database import db as db_module
from app.database.db import initialize_database


class TestCalendarUI(unittest.TestCase):

    def setUp(self):
        self.ready = False
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
        from app.theme import apply_theme, get_fonts
        from app.screens.calendar_screen import CalendarScreen

        apply_theme(self.root)
        self.screen = CalendarScreen(self.root, get_fonts())
        self.ready = True

    def tearDown(self):
        if not self.ready:
            return
        import app.config as config
        import app.utils.logging_service as ls

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.screen.destroy()
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_016_adding_event_in_another_month_jumps_to_it(self):
        today = date.today()
        target = date(today.year + 1, 12, 25)
        self.screen.date_var.set(target.isoformat())
        self.screen.title_var.set("Winter Fest")
        with mock.patch("app.screens.calendar_screen.event_service.add_event", return_value=1), \
                mock.patch("app.screens.calendar_screen.messagebox.showinfo"):
            self.screen.on_add()
        self.assertEqual((self.screen.calendar.year, self.screen.calendar.month), (target.year, 12))
        self.assertEqual(self.screen.calendar.selected, target)


if __name__ == "__main__":
    unittest.main()
