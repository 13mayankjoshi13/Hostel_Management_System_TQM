import os
import tempfile
import unittest
import tkinter as tk

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database, get_connection
from app.services import home_service, leave_service, timing_service
from app.theme import show_detail_dialog
from app.utils import session
from app.utils.validation import ValidationError


class TestTimingsAndCards(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()

        # Seed sample room and student for leave / portal tests
        conn = get_connection()
        try:
            conn.execute("INSERT INTO rooms (room_id, room_number, room_type, capacity, floor, hostel_type) VALUES (1, '101', 'Double', 2, 1, 'Boys')")
            conn.execute("INSERT INTO students (student_id, name, registration_number, contact_number, gender) VALUES (1, 'Rahul Roy', 'REG101', '9876543210', 'Male')")
            conn.execute("INSERT INTO allocations (allocation_id, student_id, room_id, status) VALUES (1, 1, 1, 'Active')")
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_default_timings(self):
        t = timing_service.get_timings()
        self.assertIn("mess_breakfast", t)
        self.assertIn("college", t)
        self.assertIn("outing", t)
        self.assertIn("returning", t)
        self.assertEqual(t["mess_breakfast"], "07:30 AM – 09:30 AM")

    def test_admin_can_save_timings(self):
        session.set_session("admin", "Administrator")
        updated = {
            "mess_breakfast": "08:00 AM – 10:00 AM",
            "mess_lunch": "01:00 PM – 03:00 PM",
            "mess_snacks": "05:30 PM – 06:30 PM",
            "mess_dinner": "08:00 PM – 10:00 PM",
            "college": "08:30 AM – 04:30 PM (Mon–Fri)",
            "outing": "04:30 PM – 09:00 PM (Daily)",
            "returning": "09:00 PM (Strict Gate In-Time)",
        }
        res = timing_service.save_timings(updated)
        self.assertEqual(res["mess_breakfast"], "08:00 AM – 10:00 AM")
        self.assertEqual(res["returning"], "09:00 PM (Strict Gate In-Time)")

        # Verify persistence
        fetched = timing_service.get_timings()
        self.assertEqual(fetched["mess_breakfast"], "08:00 AM – 10:00 AM")
        self.assertEqual(fetched["returning"], "09:00 PM (Strict Gate In-Time)")

    def test_non_admin_cannot_save_timings(self):
        session.set_session("student1", "Student", student_id=1)
        with self.assertRaises(ValidationError):
            timing_service.save_timings({"mess_breakfast": "08:00 AM – 10:00 AM"})

    def test_blank_timing_validation(self):
        session.set_session("admin", "Administrator")
        with self.assertRaises(ValidationError):
            timing_service.save_timings({"mess_breakfast": "   "})

    def test_student_return_status_when_in_hostel(self):
        status = timing_service.get_student_return_status(1)
        self.assertFalse(status["is_out"])
        self.assertEqual(status["badge"], "IN HOSTEL")
        self.assertIn("08:30 PM", status["returning_info"])

    def test_student_return_status_when_on_leave(self):
        session.set_session("warden", "Warden")
        leave_service.record_leave(1, "2026-11-01", "2026-11-05", "Visiting Family")

        status = timing_service.get_student_return_status(1)
        self.assertTrue(status["is_out"])
        self.assertEqual(status["badge"], "OUT ON LEAVE")
        self.assertEqual(status["to_date"], "2026-11-05")
        self.assertIn("2026-11-05", status["returning_info"])

    def test_student_home_includes_timings_and_return_status(self):
        session.set_session("rahul", "Student", student_id=1)
        data = home_service.student_home()
        self.assertIn("timings", data)
        self.assertIn("return_status", data)
        self.assertIn("mess_breakfast", data["timings"])
        self.assertFalse(data["return_status"]["is_out"])

    def test_show_detail_dialog_with_kwargs(self):
        root = tk.Tk()
        root.withdraw()
        try:
            dlg = show_detail_dialog(
                title="Test Dialog",
                fields={"Metric": "On leave", "Value": "2"},
                full_text="Live snapshot: On leave is 2"
            )
            self.assertIsNotNone(dlg)
            dlg.destroy()
        finally:
            root.destroy()

    def test_emergency_contact_update_and_email_support(self):
        from app.services import emergency_service
        from app.utils.validation import validate_emergency_number

        emergency_service.seed_defaults()
        emergency_service.seed_university_defaults()

        contacts = emergency_service.list_contacts()
        names = {c["name"] for c in contacts}
        self.assertIn("University Security Control", names)
        self.assertIn("Hostel Official Gmail", names)

        # Validate email acceptance
        self.assertEqual(validate_emergency_number("hostel.helpdesk@gmail.com"), "hostel.helpdesk@gmail.com")
        self.assertEqual(validate_emergency_number("admin-dept@university.edu.in"), "admin-dept@university.edu.in")
        with self.assertRaises(ValidationError):
            validate_emergency_number("invalid_email@")

        # Admin update contact
        session.set_session("admin", "Administrator")
        gmail_contact = next(c for c in contacts if c["name"] == "Hostel Official Gmail")
        emergency_service.update_contact(
            gmail_contact["contact_id"],
            "Hostel Care Desk",
            "hostelcare@university.ac.in",
            "Support"
        )
        updated_contacts = {c["contact_id"]: c for c in emergency_service.list_contacts()}
        self.assertEqual(updated_contacts[gmail_contact["contact_id"]]["name"], "Hostel Care Desk")
        self.assertEqual(updated_contacts[gmail_contact["contact_id"]]["number"], "hostelcare@university.ac.in")
        self.assertEqual(updated_contacts[gmail_contact["contact_id"]]["category"], "Support")

        # Student cannot update contact
        session.set_session("rahul", "Student", student_id=1)
        with self.assertRaises(ValidationError):
            emergency_service.update_contact(
                gmail_contact["contact_id"],
                "Hacked Name",
                "hacked@gmail.com"
            )


if __name__ == "__main__":
    unittest.main()
