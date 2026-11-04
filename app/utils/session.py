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


SUPER_ROLES = ("Super Admin",)
ADMIN_ROLES = ("Super Admin", "Administrator")
WARDEN_ROLES = ADMIN_ROLES + ("Warden",)
STAFF_ROLES = WARDEN_ROLES + ("Staff",)
SPECIALIST_ROLES = ("Mess Staff", "Maintenance Staff", "Security Staff", "Housekeeping Staff")
ALL_ROLES = STAFF_ROLES + SPECIALIST_ROLES + ("Student",)
ROLE_CATEGORIES = {"Mess Staff": ("Food",), "Maintenance Staff": ("Maintenance", "Washroom"),
                   "Housekeeping Staff": ("Cleanliness",)}
COMPLAINT_ROLES = STAFF_ROLES + tuple(ROLE_CATEGORIES)
VISITOR_ROLES = STAFF_ROLES + ("Security Staff",)
GATE_ROLES = WARDEN_ROLES + ("Security Staff",)
MESS_MANAGE_ROLES = ADMIN_ROLES + ("Mess Staff",)
MESS_VIEW_ROLES = WARDEN_ROLES + ("Mess Staff",)
CLEANING_MANAGE_ROLES = ADMIN_ROLES + ("Housekeeping Staff",)
CLEANING_VIEW_ROLES = WARDEN_ROLES + ("Housekeeping Staff",)


def handles_category(category: str) -> bool:
    """General staff handle every complaint; specialists only their own categories."""
    role = get_role()
    if role in STAFF_ROLES:
        return True
    return category in ROLE_CATEGORIES.get(role, ())


def require_roles(allowed, action: str) -> None:
    """Service-layer permission check; raises ValidationError so screens show it like any other rule."""
    if get_role() not in allowed:
        from app.utils.logging_service import log_audit
        from app.utils.validation import ValidationError
        log_audit("Security", "AccessDenied", get_user(), "Failure", f"Role '{get_role()}' tried to {action}.")
        raise ValidationError(f"Your role is not allowed to {action}.")


def require_own_or_staff(student_id, action: str) -> None:
    """Staff may act for any student; a Student session only for its own record."""
    if get_role() in STAFF_ROLES:
        return
    if get_role() == "Student" and get_student_id() == student_id:
        return
    require_roles((), action)
