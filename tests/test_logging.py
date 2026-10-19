"""Module Tests (Q09 feature #3) — Error Logs and Audit Logs."""
import csv
import os
import tempfile
import unittest

import app.utils.logging_service as ls
from app.utils import session


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TestLogging(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.error_csv = os.path.join(self.tmp, "error_logs.csv")
        self.audit_csv = os.path.join(self.tmp, "audit_logs.csv")
        self._orig = (ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self.error_csv, self.audit_csv
        session.clear_session()

    def tearDown(self):
        ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._orig
        session.clear_session()
        for p in (self.error_csv, self.audit_csv):
            if os.path.exists(p):
                os.remove(p)
        os.rmdir(self.tmp)

    def test_error_log_has_all_required_fields(self):
        ls.log_error("Student", "ValueError", "High", "add_student", message_reference="bad")
        row = _read(self.error_csv)[0]
        self.assertEqual(list(row.keys()), ls._ERROR_HEADER)
        self.assertEqual(row["module"], "Student")
        self.assertEqual(row["error_type"], "ValueError")
        self.assertEqual(row["severity"], "High")
        self.assertEqual(row["action"], "add_student")
        self.assertEqual(row["status"], "Open")
        self.assertEqual(row["message_reference"], "bad")
        self.assertTrue(row["timestamp"])

    def test_error_ids_are_sequential(self):
        first = ls.log_error("A", "E", "Low", "x")
        second = ls.log_error("A", "E", "Low", "x")
        self.assertEqual((first, second), ("ERR-0001", "ERR-0002"))

    def test_error_log_records_logged_in_user(self):
        session.set_session("warden1", "Warden")
        ls.log_error("A", "E", "Low", "x")
        self.assertEqual(_read(self.error_csv)[0]["user_id"], "warden1")

    def test_error_log_never_raises_when_unwritable(self):
        ls.ERROR_LOG_CSV = self.tmp  # a directory, cannot be opened as a file
        os.makedirs(self.tmp + ".pending")  # the fallback queue is unwritable too
        self.addCleanup(os.rmdir, self.tmp + ".pending")
        self.assertEqual(ls.log_error("A", "E", "Low", "x"), "ERR-UNLOGGED")

    def test_audit_log_has_all_required_fields(self):
        session.set_session("admin", "Administrator")
        ls.log_audit("Room", "Create", "7", "Success", "Created room 7")
        row = _read(self.audit_csv)[0]
        self.assertEqual(list(row.keys()), ls._AUDIT_HEADER)
        self.assertEqual(
            (row["user_id"], row["role"], row["module"], row["action"],
             row["record_id"], row["result"], row["description"]),
            ("admin", "Administrator", "Room", "Create", "7", "Success", "Created room 7"))
        self.assertTrue(row["timestamp"])

    def test_audit_log_is_append_only(self):
        ls.log_audit("A", "One", "1", "Success")
        ls.log_audit("A", "Two", "2", "Success")
        self.assertEqual([r["action"] for r in _read(self.audit_csv)], ["One", "Two"])

    def test_audit_log_never_raises_when_unwritable(self):
        ls.AUDIT_LOG_CSV = self.tmp
        os.makedirs(self.tmp + ".pending")
        self.addCleanup(os.rmdir, self.tmp + ".pending")
        self.assertEqual(ls.log_audit("A", "x", "1", "Success"), "unlogged")


if __name__ == "__main__":
    unittest.main()
