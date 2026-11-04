"""Specialist staff roles: each sees and does only its own work."""
import os
import tempfile
import tkinter as tk
import unittest
from datetime import date


class TestSpecialistStaff(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        self._original = (config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        db_module.initialize_database(config.DATABASE_PATH)
        from app.services import allocation_service, room_service, student_service
        self.sid = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        room = room_service.add_room("G101", "Double", 2, 0, "Girls")
        allocation_service.allocate_room(self.sid, room)
        from app.database.db import get_connection
        with get_connection() as conn:
            for cat in ("Food", "Maintenance", "Washroom", "Cleanliness"):
                conn.execute("INSERT INTO complaints (student_id, category, description) VALUES (?, ?, 'test issue here')",
                             (self.sid, cat))

    def tearDown(self):
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        from app.utils import session
        session.clear_session()
        config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original

    def login(self, role, sid=None):
        from app.utils import session
        session.set_session(role.lower().replace(" ", "_"), role, sid)

    def test_complaint_queue_is_filtered_by_role(self):
        from app.services import complaint_service as cs
        expected = {"Mess Staff": {"Food"}, "Maintenance Staff": {"Maintenance", "Washroom"},
                    "Housekeeping Staff": {"Cleanliness"}}
        for role, cats in expected.items():
            self.login(role)
            self.assertEqual({c["category"] for c in cs.get_my_queue()}, cats)
        self.login("Staff")
        self.assertEqual(len(cs.get_my_queue()), 4)

    def test_specialist_cannot_touch_other_categories(self):
        from app.services import complaint_service as cs
        from app.utils.validation import ValidationError
        self.login("Mess Staff")
        food = [c for c in cs.get_my_queue()][0]["complaint_id"]
        cs.take_complaint(food)
        cs.resolve_complaint(food, "Menu fixed")
        self.login("Maintenance Staff")
        other = next(c["complaint_id"] for c in cs.get_my_queue() if c["category"] == "Maintenance")
        self.login("Mess Staff")
        with self.assertRaises(ValidationError):
            cs.take_complaint(other)

    def test_security_has_no_complaint_or_full_list_access(self):
        from app.services import complaint_service as cs
        from app.utils.validation import ValidationError
        self.login("Security Staff")
        with self.assertRaises(ValidationError):
            cs.get_my_queue()
        with self.assertRaises(ValidationError):
            cs.get_all_complaints()
        self.login("Mess Staff")
        with self.assertRaises(ValidationError):
            cs.get_all_complaints()

    def test_visitors_and_gate_roles(self):
        from app.services import gate_service, visitor_service
        from app.utils.validation import ValidationError
        self.login("Security Staff")
        visitor_service.visit_targets()
        gate_service.log_movement(self.sid, "Out")
        self.assertEqual(gate_service.counts()["out_now"], 1)
        with self.assertRaises(ValidationError):
            gate_service.log_movement(self.sid, "Out")
        gate_service.log_movement(self.sid, "In")
        self.assertEqual(gate_service.counts()["out_now"], 0)
        for role in ("Mess Staff", "Maintenance Staff", "Housekeeping Staff", "Student"):
            self.login(role, self.sid if role == "Student" else None)
            with self.assertRaises(ValidationError):
                gate_service.log_movement(self.sid, "Out")

    def test_late_flag(self):
        from app.services import gate_service
        self.assertTrue(gate_service._is_late("2026-01-01 23:30:00"))
        self.assertTrue(gate_service._is_late("2026-01-01 03:00:00"))
        self.assertFalse(gate_service._is_late("2026-01-01 18:00:00"))

    def test_mess_menu_and_feedback(self):
        from app.services import mess_service
        from app.utils.validation import ValidationError
        today = date.today().isoformat()
        self.login("Student", self.sid)
        with self.assertRaises(ValidationError):
            mess_service.set_menu(today, "Lunch", "Dal")
        with self.assertRaises(ValidationError):
            mess_service.submit_feedback(today, "Lunch", 4, "")
        self.login("Mess Staff")
        mess_service.set_menu(today, "Lunch", "Dal, rice")
        with self.assertRaises(ValidationError):
            mess_service.submit_feedback(today, "Lunch", 4, "")
        self.login("Student", self.sid)
        mess_service.submit_feedback(today, "Lunch", 2, "Cold")
        with self.assertRaises(ValidationError):
            mess_service.submit_feedback(today, "Lunch", 9, "")
        self.login("Mess Staff")
        lunch = next(r for r in mess_service.feedback_summary() if r["meal"] == "Lunch")
        self.assertEqual(lunch["votes"], 1)
        self.assertTrue(lunch["low"])

    def test_cleaning_roles(self):
        from app.services import housekeeping_service as hk
        from app.utils.validation import ValidationError
        self.login("Housekeeping Staff")
        rows = hk.checklist()
        self.assertTrue(rows)
        r = rows[0]
        hk.set_done(r["hostel"], r["floor"], "Corridor")
        self.assertEqual(hk.progress()["done"], 1)
        hk.set_done(r["hostel"], r["floor"], "Corridor", False)
        self.assertEqual(hk.progress()["done"], 0)
        self.login("Warden")
        hk.checklist()
        with self.assertRaises(ValidationError):
            hk.set_done(r["hostel"], r["floor"], "Corridor")
        self.login("Mess Staff")
        with self.assertRaises(ValidationError):
            hk.checklist()

    def test_roles_can_be_created_and_log_in_on_staff_tab(self):
        from app.services import auth_service
        self.assertEqual(set(auth_service.LOGIN_PANELS["Staff"]) & set(("Mess Staff", "Maintenance Staff",
                         "Security Staff", "Housekeeping Staff")), {"Mess Staff", "Maintenance Staff",
                                                                   "Security Staff", "Housekeeping Staff"})

    def test_screens_open_for_every_specialist(self):
        try:
            tk.Tk().destroy()
        except tk.TclError:
            self.skipTest("no display available")
        from app.screens.main_window import MainWindow, _allowed_screens, _home_screen
        from app.utils import session
        window = MainWindow(show_splash=False)
        try:
            for child in window.winfo_children():
                if child.winfo_class() == "Toplevel":
                    child.destroy()
            for role in ("Mess Staff", "Maintenance Staff", "Security Staff", "Housekeeping Staff", "Warden", "Administrator"):
                session.set_session("u_" + role, role, None)
                window._user = {"username": "u_" + role, "role": role}
                window._enter_user_ui(window._user)
                for key in _allowed_screens(role):
                    window.show_screen(key)
                if role in session.SPECIALIST_ROLES:
                    self.assertEqual(_home_screen(role), "Duty")
                    self.assertNotIn("Complaints", _allowed_screens(role))
                    self.assertNotIn("Attendance", _allowed_screens(role))
        finally:
            session.clear_session()
            window.destroy()


if __name__ == "__main__":
    unittest.main()
