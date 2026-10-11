"""Module Tests (Q09 feature #3) — Exception Handling."""
import csv
import importlib
import os
import sys
import tempfile
import unittest
from unittest import mock

import app.utils.logging_service as ls


class TestExceptionHandler(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.error_csv = os.path.join(self.tmp, "error_logs.csv")
        self._orig = ls.ERROR_LOG_CSV
        ls.ERROR_LOG_CSV = self.error_csv

        self.messagebox = mock.MagicMock()
        fake_tk = mock.MagicMock(messagebox=self.messagebox)
        patcher = mock.patch.dict(sys.modules, {"tkinter": fake_tk, "tkinter.messagebox": self.messagebox})
        patcher.start()
        self.addCleanup(patcher.stop)
        sys.modules.pop("app.utils.exception_handler", None)
        self.handler = importlib.import_module("app.utils.exception_handler")
        self.addCleanup(sys.modules.pop, "app.utils.exception_handler", None)

    def tearDown(self):
        ls.ERROR_LOG_CSV = self._orig
        if os.path.exists(self.error_csv):
            os.remove(self.error_csv)
        os.rmdir(self.tmp)

    def test_unexpected_error_is_logged_with_type_and_message(self):
        error_id = self.handler.handle_unexpected_error("Room", "add_room", KeyError("boom"))
        with open(self.error_csv, newline="", encoding="utf-8") as f:
            row = next(csv.DictReader(f))
        self.assertEqual(error_id, row["error_id"])
        self.assertEqual((row["module"], row["error_type"], row["action"], row["severity"]),
                         ("Room", "KeyError", "add_room", "High"))
        self.assertIn("boom", row["message_reference"])

    def test_user_sees_friendly_message_without_traceback(self):
        error_id = self.handler.handle_unexpected_error("Room", "add_room", RuntimeError("secret detail"))
        title, text = self.messagebox.showerror.call_args[0]
        self.assertEqual(title, "Unexpected Error")
        self.assertIn(error_id, text)
        self.assertNotIn("secret detail", text)
        self.assertNotIn("Traceback", text)


if __name__ == "__main__":
    unittest.main()
