import os
import tempfile
import unittest
from datetime import date, timedelta

from app.database import db as db_module
from app.database.db import initialize_database, get_connection
from app.services import (allocation_service, attendance_service, leave_service, notice_service, room_service,
                           search_service, profile_service, student_service, visitor_service, complaint_service)
from app.utils import session
from app.utils.validation import ValidationError


class TestBatch84(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.utils.logging_service as ls
        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        self.boy = student_service.add_student("Arjun Rao", "AB1001", "9876543201", "Male")
        self.other = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        self.room = room_service.add_room("B101", "Double", 2, 1, "Boys")
        self.room2 = room_service.add_room("G101", "Double", 2, 1, "Girls")
        allocation_service.allocate_room(self.boy, self.room)
        allocation_service.allocate_room(self.other, self.room2)

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as ls
        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_student_leave_needs_approval(self):
        today = date.today().isoformat()
        session.set_session("arjun", "Student", self.boy)
        lid = leave_service.record_leave(self.boy, today, today, "Family")
        with self.assertRaises(ValidationError):
            leave_service.record_leave(self.boy, today, today, "Again")
        with self.assertRaises(ValidationError):
            leave_service.decide_leave(lid, True)
        session.set_session("a", "Administrator")
        self.assertEqual(attendance_service.attendance_counts(today)["Leave"], 0)
        self.assertEqual(leave_service.pending_count(), 1)
        leave_service.decide_leave(lid, True)
        self.assertEqual(attendance_service.attendance_counts(today)["Leave"], 1)
        with self.assertRaises(ValidationError):
            leave_service.decide_leave(lid, False, "late")
        session.set_session("arjun", "Student", self.boy)
        self.assertTrue(any(n["title"] == "Leave approved" for n in notice_service.notices_for_student()))

    def test_reject_needs_reason_and_staff_cannot_decide(self):
        today = date.today().isoformat()
        session.set_session("arjun", "Student", self.boy)
        lid = leave_service.record_leave(self.boy, today, today, "Trip")
        session.set_session("s", "Staff")
        with self.assertRaises(ValidationError):
            leave_service.decide_leave(lid, True)
        session.set_session("w", "Warden")
        with self.assertRaises(ValidationError):
            leave_service.decide_leave(lid, False, "")
        leave_service.decide_leave(lid, False, "Exams ongoing")
        session.set_session("arjun", "Student", self.boy)
        self.assertEqual(leave_service.record_leave(self.boy, today, today, "Retry") > lid, True)

    def test_staff_recorded_leave_is_immediate(self):
        today = date.today().isoformat()
        session.set_session("s", "Staff")
        lid = leave_service.record_leave(self.boy, today, today, "Medical")
        leaves = leave_service.get_all_leaves()
        self.assertEqual(next(l for l in leaves if l["leave_id"] == lid)["status"], "On Leave")

    def test_visitor_log(self):
        session.set_session("s", "Staff")
        vid = visitor_service.log_visitor(self.boy, "Ramesh Rao", "Parent", "9876500000", "Meeting son")
        self.assertEqual(visitor_service.inside_count(), 1)
        with self.assertRaises(ValidationError):
            visitor_service.log_visitor(self.boy, "R", "Parent", "", "x")
        with self.assertRaises(ValidationError):
            visitor_service.log_visitor(self.boy, "Ramesh", "Neighbour", "", "Meeting")
        with self.assertRaises(ValidationError):
            visitor_service.log_visitor(self.boy, "Ramesh", "Parent", "123", "Meeting")
        visitor_service.check_out(vid)
        with self.assertRaises(ValidationError):
            visitor_service.check_out(vid)
        self.assertEqual(visitor_service.inside_count(), 0)
        session.set_session("arjun", "Student", self.boy)
        with self.assertRaises(ValidationError):
            visitor_service.list_visitors()

    def test_visitor_after_hours_flag(self):
        session.set_session("s", "Staff")
        vid = visitor_service.log_visitor(self.boy, "Ramesh Rao", "Parent", "", "Late visit")
        conn = get_connection()
        conn.execute("UPDATE visitors SET in_time = '2026-01-01 21:30:00' WHERE visitor_id = ?", (vid,))
        conn.commit()
        conn.close()
        self.assertEqual(visitor_service.list_visitors()[0]["flag"], "After hours")

    def test_monthly_report(self):
        today = date.today()
        month = today.strftime("%Y-%m")
        session.set_session("a", "Administrator")
        marked = 0
        for back in range(4):
            d = today - timedelta(days=back)
            if d.strftime("%Y-%m") != month:
                continue
            attendance_service.mark_attendance(self.boy, d.isoformat(), "Present" if back == 0 else "Absent")
            marked += 1
        row = next(r for r in attendance_service.monthly_report(month) if r["student_id"] == self.boy)
        self.assertEqual(row["present"] + row["absent"], marked)
        self.assertEqual(row["percent"], round(row["present"] / marked * 100, 1))
        self.assertEqual(row["low"], row["percent"] < 75)
        path = os.path.join(self.tmp, "r.csv")
        self.assertEqual(attendance_service.export_report_csv(month, path), 2)
        with open(path, encoding="utf-8") as handle:
            self.assertIn("Arjun Rao", handle.read())
        with self.assertRaises(ValidationError):
            attendance_service.monthly_report("2999-01")
        with self.assertRaises(ValidationError):
            attendance_service.monthly_report("bad")
        session.set_session("w", "Warden")
        with self.assertRaises(ValidationError):
            attendance_service.monthly_report(month)

    def test_unread_notices(self):
        session.set_session("w", "Warden")
        notice_service.send_notice("Water cut", "No water 2-4 PM", "All")
        notice_service.send_notice("Boys only", "Curfew 10 PM", "Boys")
        session.set_session("arjun", "Student", self.boy)
        self.assertEqual(notice_service.unread_count(), 2)
        notice_service.mark_all_read()
        self.assertEqual(notice_service.unread_count(), 0)
        session.set_session("w", "Warden")
        notice_service.send_notice("New", "Fresh notice", "All")
        session.set_session("arjun", "Student", self.boy)
        self.assertEqual(notice_service.unread_count(), 1)
        session.set_session("meera", "Student", self.other)
        self.assertEqual(notice_service.unread_count(), 2)

    def test_search_respects_role(self):
        session.set_session("a", "Administrator")
        complaint_service.create_complaint(self.boy, "Maintenance", "Fan is broken in the room")
        kinds = {h["kind"] for h in search_service.search("ar")}
        self.assertIn("Student", kinds)
        self.assertEqual([h["title"] for h in search_service.search("Meera")], ["Meera Nair"])
        self.assertEqual(search_service.search("B101")[0]["kind"], "Room")
        self.assertEqual(search_service.search("fan")[0]["kind"], "Complaint")
        self.assertEqual(search_service.search("x"), [])
        session.set_session("s", "Staff")
        self.assertEqual({h["kind"] for h in search_service.search("Fan")}, {"Complaint"})
        self.assertEqual(search_service.search("Meera"), [])
        session.set_session("arjun", "Student", self.boy)
        with self.assertRaises(ValidationError):
            search_service.search("Meera")

    def test_student_profile(self):
        session.set_session("w", "Warden")
        hit = search_service.search("Meera")[0]
        self.assertEqual(hit["student_id"], self.other)
        data = profile_service.student_profile(hit["student_id"])
        self.assertEqual(data["student"]["name"], "Meera Nair")
        self.assertEqual(data["room"]["room_number"], "G101")
        self.assertEqual(data["attendance"]["Present"], 0)
        with self.assertRaises(ValidationError):
            profile_service.student_profile(9999)
        session.set_session("s", "Staff")
        with self.assertRaises(ValidationError):
            profile_service.student_profile(self.other)


if __name__ == "__main__":
    unittest.main()
