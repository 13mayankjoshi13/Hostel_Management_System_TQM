import os
import tempfile
import unittest
from datetime import date, timedelta

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import (allocation_service, attendance_service, emergency_service, leave_service,
                          notice_service, room_service, student_service, warden_service)
from app.utils import session
from app.utils.validation import ValidationError


class TestNoticesAttendance(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        self.boy = student_service.add_student("Arjun Rao", "AB1001", "9876543201", "Male")
        self.girl = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        self.boys_room = room_service.add_room("B101", "Double", 2, 1, "Boys")
        self.girls_room = room_service.add_room("G101", "Double", 2, 1, "Girls")

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_hostel_gender_rule_in_allocation(self):
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(self.girl, self.boys_room)
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(self.boy, self.girls_room)
        allocation_service.allocate_room(self.boy, self.boys_room)
        allocation_service.allocate_room(self.girl, self.girls_room)

    def test_gender_required_for_gendered_room_and_change_blocked(self):
        nogender = student_service.add_student("Sam Peter", "AB1003", "9876543203")
        with self.assertRaises(ValidationError):
            allocation_service.allocate_room(nogender, self.boys_room)
        allocation_service.allocate_room(self.boy, self.boys_room)
        with self.assertRaises(ValidationError):
            student_service.update_student(self.boy, "Arjun Rao", "AB1001", "9876543201", "Female")
        student_service.update_student(self.boy, "Arjun Rao", "AB1001", "9876543299")
        with self.assertRaises(ValidationError):
            student_service.add_student("Bad Gender", "AB1004", "9876543204", "Other")

    def test_room_floor_and_hostel_validation(self):
        for floor in (-1, 21, "x", 1.5):
            with self.assertRaises(ValidationError):
                room_service.add_room("X1", "Single", 1, floor)
        with self.assertRaises(ValidationError):
            room_service.add_room("X1", "Single", 1, 0, "Mixed")

    def test_notice_audiences(self):
        notice_service.send_notice("All hands", "Meeting at six", "All")
        notice_service.send_notice("Boys only", "Water cut tonight", "Boys")
        notice_service.send_notice("Just you", "Please see the office", "Student", self.girl)
        session.set_session("a", "Student", self.boy)
        self.assertEqual({n["title"] for n in notice_service.notices_for_student()}, {"All hands", "Boys only"})
        session.set_session("m", "Student", self.girl)
        self.assertEqual({n["title"] for n in notice_service.notices_for_student()}, {"All hands", "Just you"})
        with self.assertRaises(ValidationError):
            notice_service.notices_for_student(self.boy)
        with self.assertRaises(ValidationError):
            notice_service.send_notice("Hello", "Hi there", "All")
        with self.assertRaises(ValidationError):
            notice_service.list_notices()

    def test_notice_to_multiple_selected_students(self):
        notice_service.send_notice("Team Assembly", "Assemble in gym", "Selected Students", [self.boy, self.girl])
        session.set_session("a", "Student", self.boy)
        titles_boy = {n["title"] for n in notice_service.notices_for_student()}
        self.assertIn("Team Assembly", titles_boy)
        session.set_session("m", "Student", self.girl)
        titles_girl = {n["title"] for n in notice_service.notices_for_student()}
        self.assertIn("Team Assembly", titles_girl)
        with self.assertRaises(ValidationError):
            notice_service.send_notice("Empty team", "Nobody here", "Selected Students", [])

    def test_notice_validation_and_roles(self):
        for args in (("", "body text", "All"), ("Title", "", "All"), ("Title", "body", "Nobody"),
                     ("Title", "body", "Student"), ("Title", "body", "Student", 999)):
            with self.assertRaises(ValidationError):
                notice_service.send_notice(*args)
        session.set_session("w", "Warden")
        nid = notice_service.send_notice("Fine", "Body text", "All")
        with self.assertRaises(ValidationError):
            notice_service.delete_notice(nid)
        session.set_session("adm", "Administrator")
        notice_service.delete_notice(nid)

    def test_warden_matches_student_gender(self):
        warden_service.add_warden("Sunita Devi", "Female", "9876500001", "Girls Hostel", "9-5")
        warden_service.add_warden("Ravi Kumar", "Male", "9876500002", "Boys Hostel")
        session.set_session("a", "Student", self.girl)
        self.assertEqual(warden_service.warden_for_student()["name"], "Sunita Devi")
        session.set_session("a", "Student", self.boy)
        self.assertEqual(warden_service.warden_for_student()["name"], "Ravi Kumar")
        with self.assertRaises(ValidationError):
            warden_service.add_warden("X Y", "Male", "9876500003", "Boys Hostel")
        session.set_session("w", "Warden")
        with self.assertRaises(ValidationError):
            warden_service.add_warden("Another One", "Male", "9876500003", "Boys Hostel")

    def test_attendance_marking_and_leave(self):
        allocation_service.allocate_room(self.boy, self.boys_room)
        allocation_service.allocate_room(self.girl, self.girls_room)
        today = date.today().isoformat()
        attendance_service.mark_attendance(self.boy, today, "Present")
        attendance_service.mark_attendance(self.boy, today, "Absent")
        counts = attendance_service.attendance_counts(today)
        self.assertEqual((counts["Absent"], counts["Unmarked"]), (1, 1))
        leave_service.record_leave(self.girl, today, today, "Family function")
        self.assertEqual(attendance_service.attendance_counts(today)["Leave"], 1)
        with self.assertRaises(ValidationError):
            attendance_service.mark_attendance(self.girl, today, "Present")
        with self.assertRaises(ValidationError):
            attendance_service.mark_attendance(self.boy, (date.today() + timedelta(days=1)).isoformat(), "Present")
        with self.assertRaises(ValidationError):
            attendance_service.mark_attendance(self.boy, "31-10-2026", "Present")
        with self.assertRaises(ValidationError):
            attendance_service.mark_attendance(self.boy, today, "Late")

    def test_student_summary_and_permissions(self):
        allocation_service.allocate_room(self.boy, self.boys_room)
        today = date.today().isoformat()
        attendance_service.mark_attendance(self.boy, today, "Present")
        session.set_session("a", "Student", self.boy)
        self.assertEqual(attendance_service.student_summary()["Present"], 1)
        with self.assertRaises(ValidationError):
            attendance_service.mark_attendance(self.boy, today, "Present")
        with self.assertRaises(ValidationError):
            attendance_service.get_roster(today)
        with self.assertRaises(ValidationError):
            attendance_service.student_summary(self.girl)

    def test_emergency_numbers(self):
        emergency_service.seed_defaults()
        emergency_service.seed_defaults()
        numbers = {c["number"] for c in emergency_service.list_contacts()}
        self.assertEqual(numbers, {"112", "100", "101", "108", "1091"})
        cid = emergency_service.add_contact("Hostel Office", "+91 522 123 4567")
        for args in (("", "112"), ("X", "112"), ("Office", "abc"), ("Office", "12")):
            with self.assertRaises(ValidationError):
                emergency_service.add_contact(*args)
        emergency_service.delete_contact(cid)
        session.set_session("s", "Staff")
        with self.assertRaises(ValidationError):
            emergency_service.add_contact("Office", "112")


if __name__ == "__main__":
    unittest.main()
