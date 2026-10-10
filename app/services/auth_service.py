"""
Authentication service (Batch 9).

Roles match the stakeholders named in the project's own customer
definition: Hostel Administrator, Hostel Warden, Hostel Staff.

Passwords are never stored in plain text: PBKDF2-HMAC-SHA256 with a
random 16-byte per-user salt and 100,000 iterations, stored as
"<salt_hex>:<hash_hex>" in a single column. This is standard-library
only (hashlib) — no new dependency.
"""
import hashlib
import os
import sqlite3

from app.database.db import get_connection
from app.utils.validation import validate_username, validate_password, validate_role, ValidationError
from app.utils.logging_service import log_error, log_audit
from app.utils import session

_PBKDF2_ITERATIONS = 100_000


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return candidate.hex() == digest_hex


def create_user(username: str, password: str, role: str) -> int:
    """Validate and insert a new user account. Returns the new user_id."""
    clean_username = validate_username(username)
    clean_password = validate_password(password)
    clean_role = validate_role(role)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username = ?", (clean_username,))
        if cur.fetchone() is not None:
            raise ValidationError(f"Username '{clean_username}' is already taken.")

        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (clean_username, _hash_password(clean_password), clean_role),
        )
        conn.commit()
        user_id = cur.lastrowid
        log_audit("User", "Create", str(user_id), "Success",
                   f"Created account '{clean_username}' with role '{clean_role}'.")
        return user_id

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "create_user",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not create the account due to a database error.")
    finally:
        conn.close()


def authenticate(username: str, password: str) -> dict:
    """
    Verify credentials and, on success, start the session (so the
    audit log entry for this very login already shows the right user).
    Raises ValidationError with a single generic message on any
    failure — deliberately not revealing whether the username or the
    password was wrong.
    """
    if not username or not password:
        raise ValidationError("Enter both a username and a password.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (str(username).strip(),))
        user = cur.fetchone()

        if user is None or not _verify_password(password, user["password_hash"]):
            raise ValidationError("Invalid username or password.")

        session.set_session(user["username"], user["role"])
        log_audit("Auth", "Login", str(user["user_id"]), "Success",
                   f"'{user['username']}' logged in.")
        return {"user_id": user["user_id"], "username": user["username"], "role": user["role"]}

    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("Auth", "DatabaseError", "High", "authenticate",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not log in due to a database error.")
    finally:
        conn.close()


def logout() -> None:
    if session.is_logged_in():
        log_audit("Auth", "Logout", session.get_user(), "Success",
                   f"'{session.get_user()}' logged out.")
    session.clear_session()


def ensure_default_admin() -> None:
    """
    First-run bootstrap: if there are no user accounts yet, create one
    default Administrator so the app is usable immediately. Logged
    explicitly as a system action (not attributed to any person), since
    nobody is logged in yet when this runs.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM users")
        if cur.fetchone()["n"] > 0:
            return
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", _hash_password("admin123"), "Administrator"),
        )
        conn.commit()
        log_audit("User", "Create", "bootstrap", "Success",
                   "Default administrator account created on first run "
                   "(username: admin, password: admin123 — change this).")
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "Critical", "ensure_default_admin",
                   status="Open", message_reference=str(exc))
    finally:
        conn.close()


def list_users() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, role, created_at FROM users ORDER BY user_id")
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "list_users",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def change_password(user_id: int, new_password: str) -> None:
    clean_password = validate_password(new_password)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise ValidationError("That user account does not exist.")
        cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?",
                    (_hash_password(clean_password), user_id))
        conn.commit()
        log_audit("User", "ChangePassword", str(user_id), "Success",
                   f"Password changed for '{row['username']}'.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "change_password",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not change the password due to a database error.")
    finally:
        conn.close()


def delete_user(user_id: int) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT username, role FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise ValidationError("That user account does not exist.")
        if row["username"] == session.get_user() and session.is_logged_in():
            raise ValidationError("You cannot delete the account you are logged in with.")
        if row["role"] == "Administrator":
            cur.execute("SELECT COUNT(*) AS n FROM users WHERE role = 'Administrator'")
            if cur.fetchone()["n"] <= 1:
                raise ValidationError("Cannot delete the last remaining Administrator.")
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        log_audit("User", "Delete", str(user_id), "Success",
                   f"Deleted account '{row['username']}'.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "delete_user",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not delete the account due to a database error.")
    finally:
        conn.close()
