import os
import tempfile
import unittest
from unittest import mock

import app.utils.logging_service as ls
from app.database import db as db_module
from app.database.db import initialize_database
from app.services import fine_service, razorpay_client, student_service
from app.utils import session
from app.utils.validation import ValidationError, validate_fine_amount


class FakeRazorpay:
    """Stands in for the Razorpay HTTP API; records calls and lets a test 'pay' the link."""

    def __init__(self):
        self.links = {}
        self.calls = []

    def __call__(self, method, path, payload=None):
        self.calls.append((method, path))
        if method == "POST" and path == "/payment_links":
            link_id = f"plink_{len(self.links) + 1}"
            self.links[link_id] = {"id": link_id, "short_url": f"https://rzp.io/i/{link_id}", "status": "created",
                                   "amount": payload["amount"], "amount_paid": 0, "currency": "INR",
                                   "reference_id": payload["reference_id"], "payments": None}
            return dict(self.links[link_id])
        if method == "GET" and path.startswith("/payment_links/"):
            return dict(self.links[path.rsplit("/", 1)[1]])
        raise AssertionError((method, path))

    def pay(self, link_id, amount=None, payment_id="pay_TEST1"):
        link = self.links[link_id]
        link.update(status="paid", amount_paid=link["amount"] if amount is None else amount,
                    payments=[{"payment_id": payment_id, "status": "captured", "amount": link["amount"]}])


class TestFines(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import app.config as config

        self._original = (config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        initialize_database(config.DATABASE_PATH)
        session.clear_session()
        self.a = student_service.add_student("Ravi <b>Kumar</b>".replace("<b>", "").replace("</b>", ""), "AB1234", "9876543210")
        self.b = student_service.add_student("Sita Devi", "AB5678", "9876543211")
        self.gateway = FakeRazorpay()
        patcher = mock.patch.object(razorpay_client, "_request", self.gateway)
        patcher.start()
        self.addCleanup(patcher.stop)
        env = mock.patch.dict(os.environ, {"RAZORPAY_KEY_ID": "rzp_test_abc", "RAZORPAY_KEY_SECRET": "secret"})
        env.start()
        self.addCleanup(env.stop)

    def tearDown(self):
        import app.config as config

        config.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original
        db_module.DATABASE_PATH = self._original[0]
        session.clear_session()

    def test_amount_is_parsed_to_paise_and_bad_amounts_are_rejected(self):
        self.assertEqual(validate_fine_amount("250"), 25000)
        self.assertEqual(validate_fine_amount("₹1,250.50"), 125050)
        for bad in ("", "abc", "0", "0.99", "-5", "10.555", "50000.01", "nan", "inf", True, None):
            with self.assertRaises(ValidationError):
                validate_fine_amount(bad)

    def test_staff_issue_and_list_and_students_see_only_their_own(self):
        fine = fine_service.issue_fine(self.a, "250", "Late return after curfew")
        fine_service.issue_fine(self.b, "100", "Damaged chair")
        self.assertEqual(len(fine_service.get_all_fines()), 2)
        session.set_session("ravi", "Student", self.a)
        self.assertEqual([f["fine_id"] for f in fine_service.get_fines_for_student(self.a)], [fine])
        with self.assertRaises(ValidationError):
            fine_service.get_fines_for_student(self.b)
        for call in (lambda: fine_service.get_all_fines(), lambda: fine_service.issue_fine(self.a, "5", "Test reason"),
                     lambda: fine_service.record_cash_payment(fine), lambda: fine_service.waive_fine(fine)):
            with self.assertRaises(ValidationError):
                call()

    def test_online_payment_flow_settles_once_and_prints_a_receipt(self):
        fine = fine_service.issue_fine(self.a, "250.50", "Late return after curfew")
        session.set_session("ravi", "Student", self.a)
        url = fine_service.start_online_payment(fine)
        self.assertTrue(url.startswith("https://rzp.io/"))
        self.assertEqual(fine_service.start_online_payment(fine), url)
        self.assertEqual(sum(1 for m, p in self.gateway.calls if m == "POST"), 1)
        self.assertEqual(fine_service.check_online_payment(fine), "Unpaid")
        with self.assertRaises(ValidationError):
            fine_service.render_receipt_html(fine)
        self.gateway.pay("plink_1")
        self.assertEqual(fine_service.check_online_payment(fine), "Paid")
        self.assertEqual(fine_service.check_online_payment(fine), "Paid")
        row = fine_service.get_fines_for_student(self.a)[0]
        self.assertEqual((row["status"], row["payment_method"], row["razorpay_payment_id"]), ("Paid", "Razorpay", "pay_TEST1"))
        self.assertRegex(row["receipt_number"], r"^RCPT-\d{4}-000001$")
        page = fine_service.render_receipt_html(fine)
        self.assertIn("₹250.50", page)
        self.assertIn("pay_TEST1", page)
        path = fine_service.print_receipt(fine, folder=self.tmp)
        self.assertTrue(os.path.isfile(path))
        with self.assertRaises(ValidationError):
            fine_service.start_online_payment(fine)

    def test_payment_that_does_not_match_is_not_accepted(self):
        fine = fine_service.issue_fine(self.a, "250", "Late return after curfew")
        fine_service.start_online_payment(fine)
        self.gateway.pay("plink_1", amount=100)
        self.assertEqual(fine_service.check_online_payment(fine), "Unpaid")
        self.gateway.links["plink_1"]["amount_paid"] = 25000
        self.gateway.links["plink_1"]["reference_id"] = "FINE-99-1"
        self.assertEqual(fine_service.check_online_payment(fine), "Unpaid")
        self.gateway.links["plink_1"]["reference_id"] = f"FINE-{fine}-1"
        self.gateway.links["plink_1"]["status"] = "created"
        self.assertEqual(fine_service.check_online_payment(fine), "Unpaid")
        self.gateway.links["plink_1"].update(status="paid", payments=None)
        self.assertEqual(fine_service.check_online_payment(fine), "Paid")
        self.assertEqual(fine_service.get_all_fines()[0]["razorpay_payment_id"], "plink_1")

    def test_one_razorpay_payment_cannot_settle_two_fines(self):
        f1 = fine_service.issue_fine(self.a, "250", "Late return after curfew")
        f2 = fine_service.issue_fine(self.a, "250", "Late return after curfew")
        fine_service.start_online_payment(f1)
        fine_service.start_online_payment(f2)
        self.gateway.pay("plink_1")
        self.gateway.pay("plink_2")
        self.assertEqual(fine_service.check_online_payment(f1), "Paid")
        with self.assertRaises(ValidationError):
            fine_service.check_online_payment(f2)
        self.assertEqual({f["fine_id"]: f["status"] for f in fine_service.get_all_fines()}, {f1: "Paid", f2: "Unpaid"})

    def test_a_student_cannot_pay_or_print_for_another_student(self):
        fine = fine_service.issue_fine(self.b, "100", "Damaged chair")
        fine_service.record_cash_payment(fine)
        session.set_session("ravi", "Student", self.a)
        for call in (lambda: fine_service.start_online_payment(fine), lambda: fine_service.check_online_payment(fine),
                     lambda: fine_service.render_receipt_html(fine)):
            with self.assertRaises(ValidationError):
                call()

    def test_cash_waive_rules_and_receipt_is_html_escaped(self):
        student = student_service.add_student("Zed Ox", "AB9999", "9876543212")
        fine = fine_service.issue_fine(student, "10", "<script>alert(1)</script> broke window")
        fine_service.record_cash_payment(fine)
        with self.assertRaises(ValidationError):
            fine_service.record_cash_payment(fine)
        with self.assertRaises(ValidationError):
            fine_service.waive_fine(fine)
        page = fine_service.render_receipt_html(fine)
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;", page)
        other = fine_service.issue_fine(student, "10", "Noise after hours")
        fine_service.waive_fine(other)
        with self.assertRaises(ValidationError):
            fine_service.record_cash_payment(other)

    def test_live_keys_missing_keys_and_untrusted_links_are_refused(self):
        with mock.patch.dict(os.environ, {"RAZORPAY_KEY_ID": "rzp_live_abc"}):
            with self.assertRaises(ValidationError):
                razorpay_client._credentials()
        with mock.patch.dict(os.environ, {"RAZORPAY_KEY_ID": "", "RAZORPAY_KEY_SECRET": ""}):
            with self.assertRaises(ValidationError):
                razorpay_client._credentials()
        self.assertEqual(razorpay_client._credentials(), ("rzp_test_abc", "secret"))
        for url in ("http://rzp.io/i/x", "https://evilrzp.io/x", "https://rzp.io.evil.com/x", "file:///etc/passwd", ""):
            self.assertFalse(razorpay_client.is_trusted_url(url), url)
        self.assertTrue(razorpay_client.is_trusted_url("https://rzp.io/i/abc"))
        with self.assertRaises(ValidationError):
            fine_service.open_payment_page("https://evil.example.com/pay")


if __name__ == "__main__":
    unittest.main()
