# Razorpay test-mode setup (fine payments)

1. In the Razorpay Dashboard switch to **Test Mode** → Account & Settings → API Keys → Generate Test Key. Copy the Key Id (`rzp_test_...`) and Key Secret.
2. Give them to the app as environment variables (never commit them):

   Windows (PowerShell, once; then open a new terminal or sign out/in for the .exe):
   ```
   setx RAZORPAY_KEY_ID "rzp_test_xxxxxxxxxxxx"
   setx RAZORPAY_KEY_SECRET "your_test_secret"
   ```
   Linux/macOS: `export RAZORPAY_KEY_ID=... RAZORPAY_KEY_SECRET=...`
3. Start the app. Staff: **Fines** → issue a fine. Student: **My Fines** → select the fine → **Pay Online** (opens the Razorpay page in the browser) → pay with Razorpay's test card/UPI → back in the app click **I Have Paid — Check** → **Print Receipt**.

Razorpay test card: `4111 1111 1111 1111`, any future expiry, any CVV, any OTP. Test UPI: `success@razorpay`.

## How it works
- A **Payment Link** is created for the fine (amount in paise, `reference_id = FINE-<id>-<time>`). The same link is reused until paid.
- The app never trusts the browser or the user: **Check** fetches the link from Razorpay and marks the fine Paid only if status is `paid`, amount and amount paid equal the fine, and the reference matches. A Razorpay payment id can settle only one fine.
- Live keys (`rzp_live_...`) are refused unless `HOSTEL_ALLOW_LIVE_PAYMENTS=1`.
- Receipts are HTML files written to the system temp folder (`HostelReceipts`) and opened in the browser, which shows the print dialog (choose "Save as PDF" to keep a copy).
- If money arrives for a fine that was waived meanwhile, the app records a `PaymentAfterClose` error in the error log so it can be refunded in the Razorpay Dashboard.

## Limits
- Maximum fine ₹50,000; amounts have at most two decimals.
- No webhook: a student must click Check after paying (a desktop app has no public address for Razorpay to call).
- Test mode only has been designed for; real payments also need a business-verified Razorpay account.
