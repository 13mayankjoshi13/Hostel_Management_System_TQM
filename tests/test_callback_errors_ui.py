"""A crash inside a Tk callback must be logged and reported. Skipped when no display is available."""
import csv
import os
import tempfile
import tkinter as tk
import unittest
from unittest import mock

from app.utils.exception_handler import report_tk_callback_exception


class TestCallbackErrors(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.root.withdraw()
        self.tmp = tempfile.mkdtemp()
        import app.utils.logging_service as ls

        self._original = ls.ERROR_LOG_CSV
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        self.ls = ls

    def tearDown(self):
        self.ls.ERROR_LOG_CSV = self._original
        self.root.destroy()
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_026_exception_in_callback_is_logged_and_shown(self):
        self.root.report_callback_exception = report_tk_callback_exception

        def boom():
            raise RuntimeError("callback exploded")

        self.root.after(0, boom)
        with mock.patch("app.utils.exception_handler.messagebox.showerror") as shown:
            self.root.update()
        self.assertTrue(shown.called)
        with open(self.ls.ERROR_LOG_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["error_type"], "RuntimeError")
        self.assertEqual(rows[0]["module"], "Application")


if __name__ == "__main__":
    unittest.main()
