"""Notice, attendance and contacts screens build and show data. Skipped when no display is available."""
import os
import tempfile
import tkinter as tk
import unittest


class TestBatch77Screens(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.root.withdraw()
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        db_module.initialize_database(config.DATABASE_PATH)
        from app.utils import session

        session.clear_session()

    def tearDown(self):
        if not hasattr(self, "tmp"):
            return
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        from app.utils import session

        session.clear_session()
        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        self.root.destroy()

    def test_new_screens_build_and_show_data(self):
        from app.screens.attendance_screen import AttendanceScreen
        from app.screens.contacts_screen import ContactsScreen
        from app.screens.my_notices_screen import MyNoticesScreen
        from app.screens.notice_screen import NoticeScreen
        from app.services import (allocation_service, emergency_service, notice_service, room_service,
                                  student_service, warden_service)
        from app.theme import apply_theme, get_fonts
        from app.utils import session

        apply_theme(self.root)
        fonts = get_fonts()
        sid = student_service.add_student("Meera Nair", "AB1002", "9876543202", "Female")
        rid = room_service.add_room("G101", "Double", 2, 1, "Girls")
        allocation_service.allocate_room(sid, rid)
        warden_service.add_warden("Sunita Devi", "Female", "9876500001", "Girls Hostel")
        emergency_service.seed_defaults()
        notice_service.send_notice("Water cut", "No water at noon", "All")

        notices = NoticeScreen(self.root, fonts)
        notices.refresh()
        self.assertEqual(len(notices.tree.get_children()), 1)
        attendance = AttendanceScreen(self.root, fonts)
        attendance.refresh()
        self.assertEqual(len(attendance.tree.get_children()), 1)
        contacts = ContactsScreen(self.root, fonts)
        contacts.refresh()
        self.assertEqual(len(contacts.number_tree.get_children()), 5)
        session.set_session("meera", "Student", sid)
        contacts.refresh()
        self.assertEqual([contacts.warden_tree.item(i)["values"][1] for i in contacts.warden_tree.get_children()],
                         ["Sunita Devi"])
        mine = MyNoticesScreen(self.root, fonts)
        mine.refresh()
        self.assertTrue(mine.content.winfo_children())


if __name__ == "__main__":
    unittest.main()
