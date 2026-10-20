import builtins
import csv
import os
import tempfile
import unittest
from unittest import mock

import app.utils.logging_service as ls


class TestLogResilience(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._original = (ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")

    def tearDown(self):
        ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _locked(self, path):
        real_open = builtins.open

        def fake_open(file, mode="r", *args, **kwargs):
            if os.fspath(file) == path and mode.startswith(("a", "w")):
                raise PermissionError("file is open in Excel")
            return real_open(file, mode, *args, **kwargs)

        return mock.patch("app.utils.logging_service.open", fake_open, create=True)

    def _rows(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_bug_041_rows_written_while_the_csv_is_locked_are_kept_and_added_later(self):
        ls.log_audit("Room", "Create", "1", "Success", "first")
        with self._locked(ls.AUDIT_LOG_CSV):
            ls.log_audit("Room", "Create", "2", "Success", "=second")
            ls.log_audit("Room", "Create", "3", "Success", "third")
        self.assertEqual(len(self._rows(ls.AUDIT_LOG_CSV)), 1)
        self.assertTrue(os.path.exists(ls.AUDIT_LOG_CSV + ".pending"))
        ls.log_audit("Room", "Create", "4", "Success", "fourth")
        rows = self._rows(ls.AUDIT_LOG_CSV)
        self.assertEqual([r["record_id"] for r in rows], ["1", "2", "3", "4"])
        self.assertEqual(rows[1]["description"], "'=second")
        self.assertFalse(os.path.exists(ls.AUDIT_LOG_CSV + ".pending"))


    def test_bug_042_error_ids_never_repeat(self):
        header = ",".join(ls._ERROR_HEADER)
        with open(ls.ERROR_LOG_CSV, "wb") as f:
            f.write((header + "\n").encode())
            f.write("t,ERR-0001,Room,E,Low,u,a,Open,caf\xe9\n".encode("cp1252"))
            f.write(b"t,ERR-0003,Room,E,Low,u,a,Open,row 2 was deleted by hand\n")
        self.assertEqual(ls.log_error("Room", "E", "Low", "a"), "ERR-0004")
        with self._locked(ls.ERROR_LOG_CSV):
            self.assertEqual(ls.log_error("Room", "E", "Low", "a"), "ERR-0005")
            self.assertEqual(ls.log_error("Room", "E", "Low", "a"), "ERR-0006")
        self.assertEqual(ls.log_error("Room", "E", "Low", "a"), "ERR-0007")
        with open(ls.ERROR_LOG_CSV, "rb") as f:
            self.assertNotIn(b"\xe9", f.read())
        ids = [r["error_id"] for r in self._rows(ls.ERROR_LOG_CSV)]
        self.assertEqual(ids, ["ERR-0001", "ERR-0003", "ERR-0004", "ERR-0005", "ERR-0006", "ERR-0007"])


if __name__ == "__main__":
    unittest.main()
