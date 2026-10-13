"""Module Tests — demo data loader."""
import os
import tempfile
import unittest

import app.config as config
from app.database import seed_demo
from app.services import student_service, room_service, allocation_service, auth_service


class TestSeedDemo(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "seed.db")
        import app.utils.logging_service as ls
        self._ls = ls
        self._original = config.DATABASE_PATH
        self._orig_logs = (ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        self.audit_before = self._size(config.AUDIT_LOG_CSV)

    def tearDown(self):
        self._ls.ERROR_LOG_CSV, self._ls.AUDIT_LOG_CSV = self._orig_logs
        config.DATABASE_PATH = self._original
        from app.database import db as db_module
        db_module.DATABASE_PATH = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    @staticmethod
    def _size(path):
        return os.path.getsize(path) if os.path.exists(path) else -1

    def _seed(self):
        summary = seed_demo.run_seed(self.db)
        config.DATABASE_PATH = self.db
        from app.database import db as db_module
        db_module.DATABASE_PATH = self.db
        return summary

    def test_every_student_gets_record_room_and_account(self):
        summary = self._seed()
        total = len(seed_demo.STUDENTS)
        self.assertEqual((summary["students"], summary["allocations"], summary["accounts"]), (total, total, total))
        self.assertEqual(len(student_service.get_all_students()), total)
        self.assertEqual(len(allocation_service.get_active_allocations()), total)

    def test_real_mode_skips_sample_complaints_and_leaves(self):
        summary = seed_demo.run_seed(self.db, include_samples=False)
        self.assertEqual((summary["complaints"], summary["leaves"]), (0, 0))
        self.assertEqual(summary["students"], len(seed_demo.STUDENTS))

    def test_no_room_is_over_capacity(self):
        self._seed()
        counts = {}
        for a in allocation_service.get_active_allocations():
            counts[a["room_id"]] = counts.get(a["room_id"], 0) + 1
        capacities = {r["room_id"]: r["capacity"] for r in room_service.get_all_rooms()}
        self.assertTrue(all(n <= capacities[rid] for rid, n in counts.items()))

    def test_seeding_twice_adds_nothing(self):
        self._seed()
        again = seed_demo.run_seed(self.db)
        self.assertEqual(again["students"] + again["allocations"] + again["accounts"], 0)

    def test_usernames_are_unique_and_students_can_log_in(self):
        self._seed()
        names = [u["username"] for u in auth_service.list_users()]
        self.assertEqual(len(names), len(set(names)))
        result = auth_service.authenticate("mayank_joshi", seed_demo.DEFAULT_PASSWORD)
        self.assertEqual(result["role"], "Student")
        auth_service.logout()

    def test_real_audit_log_not_touched(self):
        self._seed()
        self.assertEqual(self._size(config.AUDIT_LOG_CSV), self.audit_before)

    def test_registration_numbers_follow_roll_pattern(self):
        self._seed()
        regs = {s["name"]: s["registration_number"] for s in student_service.get_all_students()}
        self.assertEqual(regs["Mayank Joshi"], "2410302037")
        self.assertEqual(len(set(regs.values())), len(regs))
        self.assertTrue(all(r.startswith("24103020") and len(r) == 10 for r in regs.values()))

    def test_contacts_look_like_indian_mobile_numbers(self):
        self._seed()
        for s in student_service.get_all_students():
            self.assertEqual(len(s["contact_number"]), 10)
            self.assertIn(s["contact_number"][0], "6789")

    def test_old_placeholder_students_are_upgraded_not_duplicated(self):
        seed_demo.run_seed(self.db)
        import sqlite3
        conn = sqlite3.connect(self.db)
        conn.execute("UPDATE students SET registration_number = 'DEMO' || student_id, contact_number = '0000000000'")
        conn.commit()
        conn.close()
        again = seed_demo.run_seed(self.db)
        config.DATABASE_PATH = self.db
        from app.database import db as db_module
        db_module.DATABASE_PATH = self.db
        self.assertEqual(again["updated"], len(seed_demo.STUDENTS))
        self.assertEqual(len(student_service.get_all_students()), len(seed_demo.STUDENTS))


if __name__ == "__main__":
    unittest.main()
