import os
import tempfile
import unittest
from datetime import date, timedelta

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import (allocation_service, attendance_service, emergency_service, event_service, fine_service,
                          home_service, notice_service, room_service, student_service, warden_service)
from app.utils import session
from app.utils.validation import ValidationError


class TestHome(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        self.girl = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        self.other = student_service.add_student("Kavya Rao", "AB1003", "9876543203", "Female")
        self.room = room_service.add_room("G101", "Double", 2, 1, "Girls")
        allocation_service.allocate_room(self.girl, self.room)
        allocation_service.allocate_room(self.other, self.room)

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_student_home_shows_only_own_data(self):
        today = date.today().isoformat()
        attendance_service.mark_attendance(self.girl, today, "Present")
        attendance_service.mark_attendance(self.other, today, "Absent")
        fine_service.issue_fine(self.girl, 100, "Late return")
        fine_service.issue_fine(self.other, 500, "Damage")
        warden_service.add_warden("Sunita Devi", "Female", "9876500001", "Girls Hostel")
        warden_service.add_warden("Ravi Kumar", "Male", "9876500002", "Boys Hostel")
        emergency_service.seed_defaults()
        notice_service.send_notice("Just Meera", "Please visit the office", "Student", self.girl)
        notice_service.send_notice("Just Kavya", "Please visit the office", "Student", self.other)
        event_service.add_event((date.today() + timedelta(days=3)).isoformat(), "Hostel Day", "Hostel Event")
        session.set_session("meera", "Student", self.girl)
        home = home_service.student_home()
        self.assertEqual(home["attendance"]["Present"], 1)
        self.assertEqual(home["attendance"]["Absent"], 0)
        self.assertEqual(home["fines_due_paise"], 10000)
        self.assertEqual([n["title"] for n in home["notices"]], ["Just Meera"])
        self.assertEqual(home["warden"]["name"], "Sunita Devi")
        self.assertEqual(len(home["emergency"]), 5)
        self.assertEqual(home["room"]["room_number"], "G101")
        self.assertTrue(any(e["title"] == "Hostel Day" for e in home["events"]))

    def test_home_rules(self):
        with self.assertRaises(ValidationError):
            home_service.student_home()
        session.set_session("w", "Warden")
        with self.assertRaises(ValidationError):
            home_service.student_home()
        self.assertEqual(home_service.staff_home()["attendance"]["Unmarked"], 2)
        session.set_session("s", "Student", self.girl)
        with self.assertRaises(ValidationError):
            home_service.staff_home()

    def test_floor_plan_hides_names_from_students(self):
        plan = home_service.floor_plan()
        self.assertEqual(plan[0]["taken"], 2)
        self.assertEqual(sorted(plan[0]["occupants"]), ["Kavya Rao", "Meera Nair"])
        session.set_session("meera", "Student", self.girl)
        plan = home_service.floor_plan()
        self.assertEqual((plan[0]["taken"], plan[0]["occupants"]), (2, []))
        self.assertEqual(home_service.my_room_number(), "G101")
        session.clear_session()
        session.set_session("x", "Staff")
        self.assertEqual(len(home_service.floor_plan()[0]["occupants"]), 2)


if __name__ == "__main__":
    unittest.main()
