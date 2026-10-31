"""
Hostel fines: staff issue them, students pay online (Razorpay Payment Links) or staff record cash,
and a receipt is printed for every paid fine.

Amounts are stored as whole paise. A fine becomes 'Paid' only after the payment is confirmed with
Razorpay's API (status, amount and reference all checked), never because a screen or a user says so.
"""
import html
import os
import sqlite3
import tempfile
import webbrowser
from datetime import datetime

from app.database.db import get_connection
from app.services import razorpay_client
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.timefmt import localise_rows, utc_now, utc_to_local
from app.utils.validation import (ValidationError, validate_fine_amount, validate_fine_reason,
                                  validate_record_id)

_SELECT = """
    SELECT f.fine_id, f.student_id, s.name AS student_name, s.registration_number, f.amount_paise,
           f.reason, f.status, f.created_at, f.paid_at, f.payment_method, f.razorpay_payment_id,
           f.receipt_number
    FROM fines f JOIN students s ON s.student_id = f.student_id
"""


def format_rupees(paise: int) -> str:
    return f"₹{paise // 100:,}.{paise % 100:02d}"


def _row(cur, fine_id: int) -> sqlite3.Row:
    cur.execute("SELECT * FROM fines WHERE fine_id = ?", (fine_id,))
    row = cur.fetchone()
    if row is None:
        raise ValidationError("That fine does not exist.")
    return row


def _shown(rows: list) -> list:
    for row in rows:
        row["amount"] = format_rupees(row["amount_paise"])
    return localise_rows(rows, "created_at", "paid_at")


def issue_fine(student_id: int, amount, reason: str) -> int:
    session.require_roles(session.WARDEN_ROLES, "issue fines")
    student_id = validate_record_id(student_id, "Please select a student.")
    paise = validate_fine_amount(amount)
    clean_reason = validate_fine_reason(reason)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
        if cur.fetchone() is None:
            raise ValidationError(f"No student found with ID {student_id}.")
        cur.execute("INSERT INTO fines (student_id, amount_paise, reason) VALUES (?, ?, ?)",
                    (student_id, paise, clean_reason))
        conn.commit()
        fine_id = cur.lastrowid
        log_audit("Fine", "Issue", str(fine_id), "Success",
                   f"Fine of {format_rupees(paise)} issued to student {student_id}.")
        return fine_id
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "High", "issue_fine", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the fine due to a database error.")
    finally:
        conn.close()


def get_all_fines() -> list:
    session.require_roles(session.WARDEN_ROLES, "view all fines")
    return _list(_SELECT + " ORDER BY f.fine_id DESC", ())


def get_fines_for_student(student_id: int) -> list:
    student_id = validate_record_id(student_id, "Please select a student.")
    session.require_own_or_staff(student_id, "view another student's fines")
    return _list(_SELECT + " WHERE f.student_id = ? ORDER BY f.fine_id DESC", (student_id,))


def _list(sql: str, params: tuple) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return _shown([dict(r) for r in cur.fetchall()])
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "Medium", "list_fines", status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def _next_receipt_number(fine_id: int) -> str:
    return f"RCPT-{datetime.now().year}-{fine_id:06d}"


def _mark_paid(cur, fine_id: int, method: str, payment_id: str = None) -> bool:
    """Unpaid -> Paid exactly once. Returns False when it was already settled."""
    cur.execute(
        "UPDATE fines SET status = 'Paid', paid_at = ?, payment_method = ?, razorpay_payment_id = ?, "
        "receipt_number = ? WHERE fine_id = ? AND status = 'Unpaid'",
        (utc_now(), method, payment_id, _next_receipt_number(fine_id), fine_id))
    return cur.rowcount == 1


def record_cash_payment(fine_id: int) -> None:
    session.require_roles(session.WARDEN_ROLES, "record cash payments")
    fine_id = validate_record_id(fine_id, "Please select a valid fine.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        fine = _row(cur, fine_id)
        if not _mark_paid(cur, fine_id, "Cash"):
            raise ValidationError(f"This fine is already {fine['status'].lower()}.")
        conn.commit()
        log_audit("Fine", "PayCash", str(fine_id), "Success", f"Cash received for {format_rupees(fine['amount_paise'])}.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "High", "record_cash_payment", status="Open", message_reference=str(exc))
        raise ValidationError("Could not record the payment due to a database error.")
    finally:
        conn.close()


def waive_fine(fine_id: int) -> None:
    session.require_roles(session.WARDEN_ROLES, "waive fines")
    fine_id = validate_record_id(fine_id, "Please select a valid fine.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        fine = _row(cur, fine_id)
        cur.execute("UPDATE fines SET status = 'Waived' WHERE fine_id = ? AND status = 'Unpaid'", (fine_id,))
        if cur.rowcount != 1:
            raise ValidationError(f"Only unpaid fines can be waived; this one is {fine['status'].lower()}.")
        conn.commit()
        log_audit("Fine", "Waive", str(fine_id), "Success", "Fine waived.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "High", "waive_fine", status="Open", message_reference=str(exc))
        raise ValidationError("Could not waive the fine due to a database error.")
    finally:
        conn.close()


def start_online_payment(fine_id: int) -> str:
    """Create (or reuse) the Razorpay payment link for an unpaid fine and return its URL."""
    fine_id = validate_record_id(fine_id, "Please select a valid fine.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        fine = _row(cur, fine_id)
        session.require_own_or_staff(fine["student_id"], "pay another student's fine")
        if fine["status"] != "Unpaid":
            raise ValidationError(f"This fine is already {fine['status'].lower()}.")
        if fine["razorpay_link_id"] and razorpay_client.is_trusted_url(fine["razorpay_link_url"]):
            link = razorpay_client.fetch_payment_link(fine["razorpay_link_id"])
            if link.get("status") == "created":
                return fine["razorpay_link_url"]
            if link.get("status") == "paid":
                raise ValidationError("This fine has already been paid. Use Check Payment to update it.")
        cur.execute("SELECT name, contact_number FROM students WHERE student_id = ?", (fine["student_id"],))
        student = cur.fetchone()
        link = razorpay_client.create_payment_link(
            fine["amount_paise"], f"FINE-{fine_id}-{int(datetime.now().timestamp())}",
            f"Hostel fine #{fine_id}: {fine['reason']}", student["name"], "+91" + (student["contact_number"] or ""))
        cur.execute("UPDATE fines SET razorpay_link_id = ?, razorpay_link_url = ? WHERE fine_id = ?",
                    (link["id"], link["short_url"], fine_id))
        conn.commit()
        log_audit("Fine", "PaymentLink", str(fine_id), "Success", "Online payment link created.")
        return link["short_url"]
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "High", "start_online_payment", status="Open", message_reference=str(exc))
        raise ValidationError("Could not start the payment due to a database error.")
    finally:
        conn.close()


def open_payment_page(url: str) -> None:
    if not razorpay_client.is_trusted_url(url):
        raise ValidationError("Refusing to open an untrusted payment address.")
    webbrowser.open(url)


def check_online_payment(fine_id: int) -> str:
    """Ask Razorpay whether the link was paid and settle the fine. Returns 'Paid' or 'Unpaid' (or the final status)."""
    fine_id = validate_record_id(fine_id, "Please select a valid fine.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        fine = _row(cur, fine_id)
        session.require_own_or_staff(fine["student_id"], "check another student's payment")
        if fine["status"] != "Unpaid":
            return fine["status"]
        if not fine["razorpay_link_id"]:
            raise ValidationError("No online payment has been started for this fine.")
        link = razorpay_client.fetch_payment_link(fine["razorpay_link_id"])
        listed = link.get("payments") or []
        payments = [p for p in ([listed] if isinstance(listed, dict) else listed)
                    if isinstance(p, dict) and p.get("status") in ("captured", "authorized", "paid")]
        genuine = (link.get("status") == "paid" and link.get("currency", "INR") == "INR"
                   and link.get("amount") == fine["amount_paise"]
                   and link.get("amount_paid") == fine["amount_paise"]
                   and str(link.get("reference_id", "")).startswith(f"FINE-{fine_id}-"))
        if not genuine:
            return "Unpaid"
        payment_id = (payments[0].get("payment_id") if payments else None) or link.get("id") or fine["razorpay_link_id"]
        try:
            settled = _mark_paid(cur, fine_id, "Razorpay", payment_id)
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValidationError("That Razorpay payment is already recorded against another fine.")
        if settled:
            log_audit("Fine", "PayOnline", str(fine_id), "Success", f"Razorpay payment {payment_id} confirmed.")
        else:
            log_error("Fine", "PaymentAfterClose", "High", "check_online_payment", status="Open",
                       message_reference=f"Payment {payment_id} received but fine {fine_id} was not Unpaid; refund needed.")
        return _row(cur, fine_id)["status"]
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "High", "check_online_payment", status="Open", message_reference=str(exc))
        raise ValidationError("Could not check the payment due to a database error.")
    finally:
        conn.close()


def render_receipt_html(fine_id: int) -> str:
    fine_id = validate_record_id(fine_id, "Please select a valid fine.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        fine = _row(cur, fine_id)
        session.require_own_or_staff(fine["student_id"], "print another student's receipt")
        if fine["status"] != "Paid":
            raise ValidationError("A receipt is available only for paid fines.")
        cur.execute("""SELECT s.name, s.registration_number,
                              (SELECT r.room_number FROM allocations a JOIN rooms r ON r.room_id = a.room_id
                               WHERE a.student_id = s.student_id AND a.status = 'Active') AS room
                       FROM students s WHERE s.student_id = ?""", (fine["student_id"],))
        student = cur.fetchone()
    except sqlite3.Error as exc:
        log_error("Fine", "DatabaseError", "Medium", "render_receipt", status="Open", message_reference=str(exc))
        raise ValidationError("Could not prepare the receipt due to a database error.")
    finally:
        conn.close()
    e = html.escape
    rows = [("Receipt no.", fine["receipt_number"]), ("Date", utc_to_local(fine["paid_at"])),
            ("Student", student["name"]), ("Registration no.", student["registration_number"]),
            ("Room", student["room"] or "—"), ("Fine for", fine["reason"]),
            ("Payment method", fine["payment_method"]),
            ("Payment ID", fine["razorpay_payment_id"] or "—"), ("Amount paid", format_rupees(fine["amount_paise"]))]
    body = "".join(f"<tr><th>{e(str(k))}</th><td>{e(str(v))}</td></tr>" for k, v in rows)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Receipt {e(fine['receipt_number'])}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:40px auto;max-width:560px;color:#111}}
h1{{font-size:20px;margin:0}}p.sub{{color:#555;margin:2px 0 20px}}table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:8px 6px;border-bottom:1px solid #ddd}}th{{width:40%;color:#555;font-weight:600}}
.total td{{font-weight:700;font-size:17px}}.foot{{margin-top:24px;color:#777;font-size:12px}}
@media print{{body{{margin:0}}}}</style></head><body onload="window.print()">
<h1>Hostel Management System</h1><p class="sub">Fine payment receipt</p><table>{body}</table>
<p class="foot">This is a computer-generated receipt. Test-mode payments carry no real money.</p></body></html>"""


def print_receipt(fine_id: int, folder: str = None) -> str:
    """Write the receipt to a file and open it in the browser, which shows the print dialog."""
    content = render_receipt_html(fine_id)
    folder = folder or os.path.join(tempfile.gettempdir(), "HostelReceipts")
    try:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"receipt_{int(fine_id)}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as exc:
        log_error("Fine", "FileError", "Medium", "print_receipt", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the receipt file.")
    log_audit("Fine", "PrintReceipt", str(fine_id), "Success", "Receipt generated.")
    return path
