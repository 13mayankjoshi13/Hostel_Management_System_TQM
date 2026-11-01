import csv
import math
import os
import tempfile
import unittest
from datetime import datetime, timedelta

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import get_connection, initialize_database
from app.services import (bug_service, fmea_service, poka_yoke_service, sixsigma_service, student_service,
                          taguchi_service)
from app.utils import session
from app.utils.validation import ValidationError


def _write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


class TestQualityTools(unittest.TestCase):

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

    def _logs(self, per_day):
        """per_day: [(operations, defects)] for consecutive days ending today."""
        today = datetime.now().date()
        audit, errors = [], []
        for i, (ops, defects) in enumerate(per_day):
            day = (today - timedelta(days=len(per_day) - 1 - i)).isoformat()
            audit += [{"timestamp": f"{day}T10:00:00", "module": "X"} for _ in range(ops)]
            errors += [{"timestamp": f"{day}T11:00:00", "module": "X"} for _ in range(defects)]
        _write(ls.AUDIT_LOG_CSV, ["timestamp", "module"], audit)
        _write(ls.ERROR_LOG_CSV, ["timestamp", "module"], errors)

    def test_no_logs_means_not_measured(self):
        s = sixsigma_service.summary()
        self.assertEqual((s["operations"], s["dpmo"], s["sigma"], s["enough"]), (0, None, None, False))
        self.assertFalse(sixsigma_service.control_chart()["enough"])
        self.assertFalse(sixsigma_service.variance_chart()["enough"])

    def test_dpmo_and_sigma_level_match_the_known_table(self):
        self.assertAlmostEqual(sixsigma_service.sigma_level(66807), 3.0, places=2)
        self.assertAlmostEqual(sixsigma_service.sigma_level(3.4), 6.0, places=1)
        self.assertIsNone(sixsigma_service.sigma_level(0))
        self._logs([(1000, 10)] * 5)
        s = sixsigma_service.summary()
        self.assertEqual((s["operations"], s["defects"], round(s["dpmo"])), (5000, 50, 10000))
        self.assertAlmostEqual(s["sigma"], 3.83, places=2)
        self.assertFalse(s["sigma_is_lower_bound"])

    def test_zero_defects_gives_a_lower_bound_not_infinity(self):
        self._logs([(500, 0)] * 5)
        s = sixsigma_service.summary()
        self.assertTrue(s["sigma_is_lower_bound"])
        self.assertTrue(math.isfinite(s["sigma"]))

    def test_control_chart_flags_the_bad_day_and_needs_five_days(self):
        self._logs([(100, 1)] * 4)
        self.assertFalse(sixsigma_service.control_chart()["enough"])
        self._logs([(1000, 5)] * 5 + [(1000, 40)])
        chart = sixsigma_service.control_chart()
        self.assertTrue(chart["enough"])
        self.assertEqual(len(chart["out_of_control"]), 1)
        self.assertTrue(chart["points"][-1]["out"])
        self.assertFalse(chart["points"][0]["out"])
        self.assertGreaterEqual(min(p["lcl"] for p in chart["points"]), 0)

    def test_variance_is_zero_for_a_steady_process_and_positive_otherwise(self):
        self._logs([(100, 2)] * 6)
        v = sixsigma_service.variance_chart()
        self.assertAlmostEqual(v["variance"], 0, places=12)
        self.assertEqual(len(v["rolling"]), 2)
        self._logs([(100, 1), (100, 9), (100, 2), (100, 12), (100, 0), (100, 7)])
        self.assertGreater(sixsigma_service.variance_chart()["variance"], 0)

    def test_quality_measures_are_admin_only(self):
        for role in ("Warden", "Staff", "Student"):
            session.set_session("x", role, 1 if role == "Student" else None)
            for call in (sixsigma_service.summary, sixsigma_service.variance_chart, taguchi_service.analyse,
                         fmea_service.list_fmea, fmea_service.list_sipoc, poka_yoke_service.list_controls):
                with self.assertRaises(ValidationError):
                    call()

    def _complaint(self, category, hours):
        sid = student_service.add_student("Kid One", "AB%04d" % (hash((category, hours)) % 10000), "9876543210")
        created = datetime(2026, 1, 5, 9, 0, 0)
        conn = get_connection()
        conn.execute("INSERT INTO complaints (student_id, category, description, status, created_at, resolved_at) "
                     "VALUES (?, ?, 'x', 'Resolved', ?, ?)",
                     (sid, category, created.strftime("%Y-%m-%d %H:%M:%S"),
                      (created + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def test_taguchi_sn_and_loss(self):
        self.assertIsNone(taguchi_service.analyse()["overall"])
        for hours in (24, 48, 72):
            self._complaint("Electrical", hours)
        self._complaint("Plumbing", 24)
        a = taguchi_service.analyse()
        mean_sq = (1 + 4 + 9 + 1) / 4
        self.assertAlmostEqual(a["overall"]["sn"], -10 * math.log10(mean_sq), places=6)
        self.assertAlmostEqual(a["overall"]["loss_share"], mean_sq / 9, places=6)
        self.assertIsNone(a["overall"]["loss_rupees"])
        self.assertTrue(a["categories"]["Plumbing"]["few"])
        self.assertFalse(a["categories"]["Electrical"]["few"])
        taguchi_service.set_assumptions("2", "900")
        self.assertAlmostEqual(taguchi_service.analyse()["overall"]["loss_rupees"], mean_sq / 4 * 900, places=4)
        taguchi_service.set_assumptions("2", "")
        self.assertIsNone(taguchi_service.get_assumptions()["cost"])

    def test_taguchi_assumption_validation(self):
        for tol, cost in (("0", ""), ("abc", ""), ("400", ""), ("3", "-5"), ("3", "x"), ("3", "0")):
            with self.assertRaises(ValidationError):
                taguchi_service.set_assumptions(tol, cost)

    def test_fmea_rpn_order_validation_and_bug_evidence(self):
        fmea_service.add_fmea("Allocation", "Room double-booked", "Two students one bed", "No capacity check", 8, 3, 4,
                              module="Allocation")
        fmea_service.add_fmea("Fines", "Wrong amount", "Overcharge", "Typing error", 9, 5, 3)
        rows = fmea_service.list_fmea()
        self.assertEqual([r["rpn"] for r in rows], [135, 96])
        self.assertTrue(rows[0]["act"])
        self.assertFalse(rows[1]["act"])
        self.assertIsNone(rows[0]["bugs_logged"] if rows[0]["module"] is None else None)
        bug_service.log_bug("Allocation", "Functional", "Capacity check off by one", "Room accepted one more student than its capacity.", "High", "High")
        self.assertEqual([r["bugs_logged"] for r in fmea_service.list_fmea() if r["module"]], [1])
        for args in ((0, 1, 1), (11, 1, 1), ("x", 1, 1), (1, 1, 1.5)):
            with self.assertRaises(ValidationError):
                fmea_service.add_fmea("S", "Mode", "Effect", "Cause", *args)
        with self.assertRaises(ValidationError):
            fmea_service.add_fmea("", "Mode", "Effect", "Cause", 1, 1, 1)
        fmea_service.update_ratings(rows[1]["fmea_id"], 10, 10, 10)
        self.assertEqual(fmea_service.list_fmea()[0]["rpn"], 1000)
        fmea_service.delete_fmea(rows[1]["fmea_id"])
        with self.assertRaises(ValidationError):
            fmea_service.delete_fmea(rows[1]["fmea_id"])

    def test_sipoc_seed_once_and_edit(self):
        fmea_service.ensure_default_sipoc()
        fmea_service.ensure_default_sipoc()
        rows = fmea_service.list_sipoc()
        self.assertEqual(len(rows), 8)
        fmea_service.add_sipoc("A", "B", "C", "D", "E")
        fmea_service.delete_sipoc(rows[0]["sipoc_id"])
        self.assertEqual(len(fmea_service.list_sipoc()), 8)
        with self.assertRaises(ValidationError):
            fmea_service.add_sipoc("", "B", "C", "D", "E")

    def test_every_poka_yoke_control_points_at_a_real_test(self):
        controls = poka_yoke_service.list_controls()
        self.assertGreaterEqual(len(controls), 10)
        missing = [c["test"] for c in controls if not c["proven"]]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
