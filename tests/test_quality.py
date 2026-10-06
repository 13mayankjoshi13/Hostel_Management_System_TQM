"""
Module Tests (Q09 feature #3) — Quality Monitoring / SQC data prep.

Covers get_quality_summary, get_pareto_data, and get_fishbone_data
against real (temp-isolated) bug records, plus the empty-data case so
the UI's "not enough data yet" path is exercised honestly.
"""
import os
import tempfile
import unittest

from app.database import db as db_module
from app.database.db import initialize_database
from app.services import bug_service, quality_service


class TestQualityMonitoring(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_hostel.db")
        self.tmp_error_csv = os.path.join(self.tmp_dir, "test_error_logs.csv")
        self.tmp_audit_csv = os.path.join(self.tmp_dir, "test_audit_logs.csv")
        self.tmp_defect_csv = os.path.join(self.tmp_dir, "test_defect_log.csv")

        import app.config as config
        import app.utils.logging_service as logging_service

        self._original_db_path = config.DATABASE_PATH
        self._original_error_csv = logging_service.ERROR_LOG_CSV
        self._original_audit_csv = logging_service.AUDIT_LOG_CSV
        self._original_defect_csv = logging_service.DEFECT_LOG_CSV

        config.DATABASE_PATH = self.tmp_db
        db_module.DATABASE_PATH = self.tmp_db
        bug_service.get_connection.__globals__["DATABASE_PATH"] = self.tmp_db

        logging_service.ERROR_LOG_CSV = self.tmp_error_csv
        logging_service.AUDIT_LOG_CSV = self.tmp_audit_csv
        logging_service.DEFECT_LOG_CSV = self.tmp_defect_csv

        initialize_database(self.tmp_db)

    def tearDown(self):
        import app.config as config
        import app.utils.logging_service as logging_service

        config.DATABASE_PATH = self._original_db_path
        db_module.DATABASE_PATH = self._original_db_path
        logging_service.ERROR_LOG_CSV = self._original_error_csv
        logging_service.AUDIT_LOG_CSV = self._original_audit_csv
        logging_service.DEFECT_LOG_CSV = self._original_defect_csv

        for path in (self.tmp_db, self.tmp_error_csv, self.tmp_audit_csv, self.tmp_defect_csv):
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.tmp_dir)

    # ---- empty state ----

    def test_quality_summary_empty(self):
        summary = quality_service.get_quality_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["fix_rate_pct"], 0)

    def test_pareto_data_empty(self):
        self.assertEqual(quality_service.get_pareto_data(), [])

    def test_fishbone_data_empty_has_all_branches(self):
        data = quality_service.get_fishbone_data()
        self.assertEqual(set(data.keys()), set(quality_service.FISHBONE_BRANCHES))
        self.assertTrue(all(causes == [] for causes in data.values()))

    # ---- with real data ----

    def test_quality_summary_counts(self):
        id1 = bug_service.log_bug("Room", "Functional", "Bug one title here",
                                   "Description one here.", "High", "High")
        bug_service.log_bug("UI", "UI/UX", "Bug two title here",
                             "Description two here.", "Low", "Low")
        bug_service.start_progress(id1)

        summary = quality_service.get_quality_summary()
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["open"], 1)
        self.assertEqual(summary["in_progress"], 1)

    def test_pareto_data_sorted_descending_with_cumulative(self):
        bug_service.log_bug("Room", "Functional", "Bug one title here", "Desc.", "High", "High")
        bug_service.log_bug("Room", "Functional", "Bug two title here", "Desc.", "High", "High")
        bug_service.log_bug("UI", "UI/UX", "Bug three title here", "Desc.", "Low", "Low")

        pareto = quality_service.get_pareto_data()
        self.assertEqual(pareto[0][0], "Functional")
        self.assertEqual(pareto[0][1], 2)
        self.assertEqual(pareto[-1][2], 100.0)  # cumulative % always ends at 100

    def test_fishbone_data_maps_category_to_branch(self):
        bug_service.log_bug("Room", "Data Integrity", "Capacity count mismatch",
                             "Allocation count does not match active rows.", "High", "High")
        data = quality_service.get_fishbone_data()
        self.assertIn("Capacity count mismatch", data["Database"])

    def test_fishbone_data_unmapped_category_falls_back_to_measurement(self):
        bug_service.log_bug("Other", "Other", "Something uncategorized here",
                             "Not sure where this belongs yet.", "Low", "Low")
        data = quality_service.get_fishbone_data()
        self.assertIn("Something uncategorized here", data["Measurement"])


if __name__ == "__main__":
    unittest.main()
