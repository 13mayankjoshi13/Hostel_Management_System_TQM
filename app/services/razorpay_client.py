"""
Minimal Razorpay client (Payment Links API) using only the standard library.

Keys come from the environment, never from the repository:
    RAZORPAY_KEY_ID      e.g. rzp_test_xxxxxxxxxxxx
    RAZORPAY_KEY_SECRET  the matching secret
Only test-mode keys (rzp_test_...) are accepted unless HOSTEL_ALLOW_LIVE_PAYMENTS=1 is set.
"""
import base64
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

from app.utils.logging_service import log_error
from app.utils.validation import ValidationError

API_BASE = "https://api.razorpay.com/v1"
TIMEOUT_SECONDS = 15
_TRUSTED_HOSTS = ("razorpay.com", "rzp.io")


def _credentials() -> tuple:
    key_id = os.environ.get("RAZORPAY_KEY_ID", "").strip()
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()
    if not key_id or not key_secret:
        raise ValidationError("Online payment is not set up. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET "
                              "(see docs/RAZORPAY_SETUP.md).")
    if key_id.startswith("rzp_live_") and os.environ.get("HOSTEL_ALLOW_LIVE_PAYMENTS") != "1":
        raise ValidationError("Live Razorpay keys are blocked. Use test keys (rzp_test_...) for now.")
    if not key_id.startswith(("rzp_test_", "rzp_live_")):
        raise ValidationError("RAZORPAY_KEY_ID does not look like a Razorpay key.")
    return key_id, key_secret


def _request(method: str, path: str, payload: dict = None) -> dict:
    key_id, key_secret = _credentials()
    token = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(API_BASE + path, data=data, method=method, headers={
        "Authorization": f"Basic {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("description", "")
        except Exception:
            pass
        log_error("Payment", "RazorpayHTTPError", "High", f"{method} {path}",
                   status="Open", message_reference=f"HTTP {exc.code}: {detail}")
        if exc.code in (401, 403):
            raise ValidationError("Razorpay rejected the keys. Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")
        raise ValidationError(f"Razorpay could not process the request ({detail or 'HTTP ' + str(exc.code)}).")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        log_error("Payment", "RazorpayNetworkError", "High", f"{method} {path}",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not reach Razorpay. Check the internet connection and try again.")


def create_payment_link(amount_paise: int, reference_id: str, description: str,
                        customer_name: str, customer_contact: str) -> dict:
    link = _request("POST", "/payment_links", {
        "amount": amount_paise,
        "currency": "INR",
        "accept_partial": False,
        "reference_id": reference_id,
        "description": description[:2000],
        "customer": {"name": customer_name, "contact": customer_contact},
        "notify": {"sms": False, "email": False},
        "reminder_enable": False,
    })
    if not link.get("id") or not is_trusted_url(link.get("short_url", "")):
        raise ValidationError("Razorpay returned an unexpected response. Try again.")
    return {"id": link["id"], "short_url": link["short_url"]}


def fetch_payment_link(link_id: str) -> dict:
    return _request("GET", f"/payment_links/{link_id}")


def is_trusted_url(url: str) -> bool:
    parts = urlparse(url or "")
    host = parts.hostname or ""
    return parts.scheme == "https" and any(host == h or host.endswith("." + h) for h in _TRUSTED_HOSTS)
