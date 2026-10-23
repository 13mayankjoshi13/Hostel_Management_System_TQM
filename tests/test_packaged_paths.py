import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCRIPT = (
    "import sys; sys.frozen = True; sys.path.insert(0, {root!r}); "
    "import app.config as c; print(c.DATABASE_PATH); print(c.ERROR_LOG_CSV)"
)


class TestPackagedPaths(unittest.TestCase):

    def test_bug_050_packaged_exe_keeps_data_in_the_user_profile(self):
        with tempfile.TemporaryDirectory() as profile:
            env = dict(os.environ, LOCALAPPDATA=profile)
            out = subprocess.run([sys.executable, "-c", SCRIPT.format(root=ROOT)], env=env,
                                 capture_output=True, text=True, check=True).stdout.split("\n")
            database, error_log = out[0], out[1]
            self.assertTrue(database.startswith(profile), database)
            self.assertTrue(error_log.startswith(profile), error_log)
            self.assertTrue(os.path.isdir(os.path.dirname(error_log)))

    def test_bug_050_source_run_still_uses_the_project_folders(self):
        import app.config as config
        self.assertTrue(config.DATABASE_PATH.startswith(os.path.join(ROOT, "app", "database")))
        self.assertTrue(config.ERROR_LOG_CSV.startswith(os.path.join(ROOT, "TQM", "data")))


if __name__ == "__main__":
    unittest.main()
