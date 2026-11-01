import csv
import os
import tempfile
import unittest

import app.utils.logging_service as ls
from app import theme
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import audit_service, settings_service, student_service
from app.utils import session
from app.utils.validation import ValidationError


class TestSettings(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()
        theme.set_appearance("Light", theme.DEFAULT_ACCENT)

    def test_appearance_is_saved_per_user_with_last_choice_fallback(self):
        self.assertEqual(settings_service.get_appearance(), settings_service.DEFAULT)
        session.set_session("asha", "Administrator")
        settings_service.set_appearance("Dark", "#0f9d8a")
        self.assertEqual(settings_service.get_appearance("asha"), ("Dark", "#0F9D8A"))
        self.assertEqual(settings_service.get_appearance(), ("Dark", "#0F9D8A"))
        session.set_session("ravi", "Staff")
        settings_service.set_appearance("Light", "#D6336C")
        self.assertEqual(settings_service.get_appearance("asha"), ("Dark", "#0F9D8A"))
        self.assertEqual(settings_service.get_appearance("new_user"), ("Light", "#D6336C"))

    def test_appearance_validation(self):
        session.set_session("asha", "Staff")
        for mode, accent in (("Blue", "#5B50E6"), ("Dark", "red"), ("Dark", "#12345"), ("Dark", "#FFFF99"),
                             ("Light", ""), ("Light", None)):
            with self.assertRaises(ValidationError):
                settings_service.set_appearance(mode, accent)
        session.clear_session()
        with self.assertRaises(ValidationError):
            settings_service.set_appearance("Dark", "#5B50E6")

    def test_palette_switches_and_every_preset_keeps_white_text_readable(self):
        theme.set_appearance("Dark", "#0F9D8A")
        self.assertEqual(theme.COLORS["background"], "#12141C")
        self.assertEqual(theme.COLORS["accent"], "#0F9D8A")
        self.assertEqual(theme.COLORS["card_bg"], theme.COLORS["surface"])
        theme.set_appearance("Light", theme.DEFAULT_ACCENT)
        self.assertEqual(theme.COLORS["background"], "#F3F5FA")
        for name, accent in theme.ACCENT_PRESETS.items():
            settings_service.validate_appearance("Light", accent)
            self.assertLess(theme.luminance(accent), 0.45, name)

    def test_audit_log_viewer_is_admin_only_and_filters(self):
        ls.log_audit("Student", "Create", "1", "Success", "Added Meera")
        ls.log_audit("Room", "Create", "2", "Failure", "Duplicate room")
        self.assertEqual(len(audit_service.read_audit_log()), 2)
        self.assertEqual(audit_service.read_audit_log(module="Room")[0]["description"], "Duplicate room")
        self.assertEqual(len(audit_service.read_audit_log(search="meera")), 1)
        self.assertEqual(audit_service.audit_modules(), ["Room", "Student"])
        for role in ("Warden", "Staff", "Student"):
            session.set_session("x", role, 1 if role == "Student" else None)
            with self.assertRaises(ValidationError):
                audit_service.read_audit_log()

    def test_missing_audit_file_is_empty(self):
        self.assertEqual(audit_service.read_audit_log(), [])

    def test_student_download_is_admin_only_audited_and_safe(self):
        student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        student_service.add_student("Arjun Rao", "AB1001", "9876543201")
        path = os.path.join(self.tmp, "s.csv")
        self.assertEqual(audit_service.export_students_csv(path), 2)
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0][:3], ["ID", "Name", "Registration No."])
        self.assertEqual(rows[1][1], "Meera Nair")
        self.assertEqual(rows[2][4], "")
        self.assertTrue(any(r["action"] == "Export" for r in audit_service.read_audit_log()))
        session.set_session("w", "Warden")
        with self.assertRaises(ValidationError):
            audit_service.export_students_csv(path)
        session.set_session("a", "Administrator")
        with self.assertRaises(ValidationError):
            audit_service.export_students_csv(os.path.join(self.tmp, "no_such_dir", "s.csv"))


if __name__ == "__main__":
    unittest.main()
