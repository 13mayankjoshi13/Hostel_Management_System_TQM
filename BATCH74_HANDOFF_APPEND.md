
## Update – Fines/Razorpay and Workers (append; do not replace the file)

New tables: `fines` (amounts in paise; Unpaid/Paid/Waived; unique `razorpay_payment_id` and `receipt_number`), `workers`, `worker_attendance`.
New services: `razorpay_client` (stdlib urllib, Payment Links, keys from `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET`, test keys only unless `HOSTEL_ALLOW_LIVE_PAYMENTS=1`), `fine_service`, `worker_service`. `student_portal_service.my_fines()`.
New screens: Fines and Workers (staff), My Fines (student). Complaint assignment now offers a list of active workers.
Rules: a fine is marked Paid only after Razorpay's API confirms status, amount and reference; students act only on their own fines (`require_own_or_staff`); receipts only for paid fines; payment URLs opened only if https on razorpay.com/rzp.io.
Not verified against the live Razorpay API from the build machine (no network access); tests use a fake gateway. Suite: 275 tests.
Features, not defects: not counted in the bug tracker.
