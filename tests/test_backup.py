import os
import sqlite3
import tempfile
import unittest

from app.database import backup, db as db_module
from app.database.db import initialize_database
import app.utils.logging_service as ls


class TestBackup(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "hostel.db")
        self._original = (ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(self.db)
        conn = sqlite3.connect(self.db)
        conn.execute("INSERT INTO students (name, registration_number, contact_number) VALUES ('Kid', 'AB123', '9876500000')")
        conn.commit()
        conn.close()

    def tearDown(self):
        ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        for root, _, files in os.walk(self.tmp, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)

    def _count(self, path):
        conn = sqlite3.connect(path)
        try:
            return conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        finally:
            conn.close()

    def test_bug_031_backup_is_created_once_per_day_and_restorable(self):
        first = backup.create_backup(self.db)
        self.assertTrue(os.path.exists(first))
        self.assertIsNone(backup.create_backup(self.db))
        conn = sqlite3.connect(self.db)
        conn.execute("DELETE FROM students")
        conn.commit()
        conn.close()
        self.assertEqual(self._count(self.db), 0)
        backup.restore_backup(first, self.db)
        self.assertEqual(self._count(self.db), 1)
        self.assertTrue(os.path.exists(self.db + ".before_restore"))

    def test_bug_031_only_the_newest_backups_are_kept(self):
        folder = backup.backup_dir(self.db)
        os.makedirs(folder)
        for day in range(1, 11):
            with open(os.path.join(folder, f"hostel_202001{day:02d}_000000.db"), "wb") as f:
                f.write(b"x")
        backup.create_backup(self.db, keep=3)
        kept = backup.list_backups(self.db)
        self.assertEqual(len(kept), 3)
        self.assertTrue(kept[-1].endswith(".db") and "2020" not in os.path.basename(kept[-1]))

    def test_bug_031_damaged_database_is_not_backed_up_and_bad_backup_not_restored(self):
        with open(self.db, "wb") as f:
            f.write(b"this is not a database" * 100)
        self.assertIsNone(backup.create_backup(self.db))
        self.assertEqual(backup.list_backups(self.db), [])
        with open(os.path.join(self.tmp, "bad.db"), "wb") as f:
            f.write(b"junk" * 100)
        with self.assertRaises(ValueError):
            backup.restore_backup(os.path.join(self.tmp, "bad.db"), self.db)

    def test_bug_043_foreign_sqlite_file_is_not_restored_and_failed_backup_leaves_nothing(self):
        other = os.path.join(self.tmp, "other.db")
        conn = sqlite3.connect(other)
        conn.execute("CREATE TABLE notes (x)")
        conn.commit()
        conn.close()
        with self.assertRaises(ValueError):
            backup.restore_backup(other, self.db)
        self.assertEqual(self._count(self.db), 1)

        original = sqlite3.connect

        class Boom:
            def __init__(self, real):
                self.real = real
            def backup(self, dest):
                raise sqlite3.OperationalError("disk full")
            def close(self):
                self.real.close()

        calls = []
        def fake(path, *a, **k):
            conn = original(path, *a, **k)
            calls.append(path)
            return Boom(conn) if path == self.db and len(calls) == 2 else conn
        backup.sqlite3.connect = fake
        try:
            with self.assertRaises(sqlite3.OperationalError):
                backup.create_backup(self.db)
        finally:
            backup.sqlite3.connect = original
        self.assertEqual(backup.list_backups(self.db), [])


if __name__ == "__main__":
    unittest.main()
