"""The app must tell the user when it cannot start, not exit silently."""
import os
import tempfile
import unittest
from unittest import mock

import app.main as app_main


class TestStartupErrors(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch("app.database.backup.create_backup", return_value=None)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tmp = tempfile.mkdtemp()
        import app.utils.logging_service as ls

        self.ls = ls
        self._original = ls.ERROR_LOG_CSV
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")

    def tearDown(self):
        self.ls.ERROR_LOG_CSV = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def test_bug_027_unopenable_database_is_shown_to_the_user(self):
        with mock.patch.object(app_main, "initialize_database", side_effect=OSError("disk I/O error")), \
                mock.patch.object(app_main, "show_fatal") as shown:
            app_main.run()
        self.assertTrue(shown.called)
        self.assertIn("disk I/O error", shown.call_args[0][1])
        self.assertIn("ERR-", shown.call_args[0][1])
        with open(self.ls.ERROR_LOG_CSV, encoding="utf-8") as f:
            self.assertIn("initialize_database", f.read())

    def test_bug_027_real_corrupt_file_triggers_the_message(self):
        import app.database.db as db_module

        bad = os.path.join(self.tmp, "bad.db")
        with open(bad, "wb") as f:
            f.write(b"this is not a sqlite database" * 50)
        original = db_module.DATABASE_PATH
        db_module.DATABASE_PATH = bad
        try:
            with mock.patch.object(app_main, "initialize_database",
                                   side_effect=lambda: db_module.initialize_database(bad)), \
                    mock.patch.object(app_main, "show_fatal") as shown:
                app_main.run()
        finally:
            db_module.DATABASE_PATH = original
        self.assertTrue(shown.called)


if __name__ == "__main__":
    unittest.main()
