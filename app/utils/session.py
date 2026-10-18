"""
Runtime session state (Batch 9: Authentication).

Before this batch, every audit/error/defect log entry was hard-coded to
CURRENT_USER/CURRENT_ROLE in app/config.py. Now those are only a
fallback for code paths that run with nobody logged in (e.g. a direct
service call from a test or script) — logging_service reads the ACTUAL
logged-in user from here at call time.

This is intentionally plain module-level state, not a class: the
application is single-user-at-a-time per process (one Tkinter window,
one person using it), so there is exactly one "current session" for the
lifetime of the running app.
"""
from app.config import CURRENT_USER as _FALLBACK_USER, CURRENT_ROLE as _FALLBACK_ROLE

_username = None
_role = None
_student_id = None


def set_session(username: str, role: str, student_id: int = None) -> None:
    global _username, _role, _student_id
    _username = username
    _role = role
    _student_id = student_id


def clear_session() -> None:
    global _username, _role, _student_id
    _username = None
    _role = None
    _student_id = None


def get_student_id():
    return _student_id


def is_logged_in() -> bool:
    return _username is not None


def get_user() -> str:
    return _username or _FALLBACK_USER


def get_role() -> str:
    return _role or _FALLBACK_ROLE


STAFF_ROLES = ("Administrator", "Warden", "Staff")


def require_roles(allowed, action: str) -> None:
    """Service-layer permission check; raises ValidationError so screens show it like any other rule."""
    if get_role() not in allowed:
        from app.utils.validation import ValidationError
        raise ValidationError(f"Your role is not allowed to {action}.")
