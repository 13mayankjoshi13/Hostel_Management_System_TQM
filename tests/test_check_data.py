import os
import sqlite3
import tempfile
import unittest

from app.database import check_data
from app.database.db import initialize_database
import app.utils.logging_service as ls


class TestCheckData(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "t.db")
        self._original = ls.ERROR_LOG_CSV
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        initialize_database(self.db)

    def tearDown(self):
        ls.ERROR_LOG_CSV = self._original
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _sql(self, *statements):
        conn = sqlite3.connect(self.db)
        for statement in statements:
            conn.execute(statement)
        conn.commit()
        conn.close()

    def test_bug_034_clean_database_has_no_issues(self):
        self._sql("INSERT INTO students (name, registration_number, contact_number) VALUES ('Kid A', 'AB123', '9876500000')",
                  "INSERT INTO rooms (room_number, room_type, capacity) VALUES ('A101', 'Double', 2)",
                  "INSERT INTO allocations (student_id, room_id) VALUES (1, 1)")
        self.assertEqual(check_data.run_checks(self.db), [])

    def test_bug_034_existing_bad_records_are_reported(self):
        self._sql(
            "DROP INDEX ux_registration_number_nocase", "DROP INDEX ux_one_active_room_per_student",
            "INSERT INTO students (name, registration_number, contact_number) VALUES ('Kid A', 'ab123', '9876500000')",
            "INSERT INTO students (name, registration_number, contact_number) VALUES ('Kid B', 'AB123', '12')",
            "INSERT INTO rooms (room_number, room_type, capacity) VALUES ('A101', 'Single', 1)",
            "INSERT INTO allocations (student_id, room_id) VALUES (1, 1)",
            "INSERT INTO allocations (student_id, room_id) VALUES (2, 1)",
            "INSERT INTO allocations (student_id, room_id) VALUES (2, 1)",
            "INSERT INTO complaints (student_id, category, description) VALUES (99, 'Maintenance', 'Tap leaking badly')",
        )
        titles = {title for title, _ in check_data.run_checks(self.db)}
        self.assertIn("Duplicate registration numbers (ignoring case)", titles)
        self.assertIn("Rooms holding more students than their capacity", titles)
        self.assertIn("Students with more than one active room", titles)
        self.assertIn("Complaints pointing at a missing student", titles)
        self.assertIn("Student contact number that today's rules reject", titles)

    def test_bug_034_issues_are_written_to_the_error_log(self):
        check_data.log_issues([("Some problem", "detail")])
        with open(ls.ERROR_LOG_CSV, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("DataQuality", text)
        self.assertIn("Some problem: detail", text)


if __name__ == "__main__":
    unittest.main()
