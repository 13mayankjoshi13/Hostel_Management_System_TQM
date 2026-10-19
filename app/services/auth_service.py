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
from datetime import datetime, timedelta

from app.database.db import get_connection
from app.utils.validation import (
    validate_record_id,validate_username, validate_password, validate_role,
                                    validate_registration_number, validate_contact_number, ValidationError)
from app.utils.logging_service import log_error, log_audit
from app.utils import session

DEFAULT_ADMIN_PASSWORD = "admin123"
SEED_PASSWORD = "Welcome123"
KNOWN_DEFAULT_PASSWORDS = (DEFAULT_ADMIN_PASSWORD, SEED_PASSWORD)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
MAX_SIGNUP_FAILURES = 5
SIGNUP_LOCKOUT_MINUTES = 15
LOGIN_FAILED_MESSAGE = (f"Invalid username or password. An account is locked for {LOCKOUT_MINUTES} minutes "
                        f"after {MAX_FAILED_ATTEMPTS} failed attempts.")
_DUMMY_HASH = None

_PBKDF2_ITERATIONS = 100_000


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def _dummy_hash() -> str:
    """Hash checked for unknown or locked accounts, so those attempts take as long as a real one."""
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = _hash_password("not-a-real-password-1")
    return _DUMMY_HASH


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return candidate.hex() == digest_hex


def create_user(username: str, password: str, role: str, student_id: int = None,
                must_change_password: bool = False) -> int:
    """Validate and insert a new user account. Student accounts must link to a student record."""
    session.require_roles(("Administrator",), "create accounts")
    clean_username = validate_username(username)
    clean_password = validate_password(password)
    clean_role = validate_role(role)
    if clean_role != "Student" and student_id is not None:
        raise ValidationError("Only Student accounts can be linked to a student record.")
    if clean_role == "Student" and student_id is None:
        raise ValidationError("A Student account must be linked to a student record.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", (clean_username,))
        if cur.fetchone() is not None:
            raise ValidationError(f"Username '{clean_username}' is already taken.")
        if clean_role == "Student":
            cur.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            if cur.fetchone() is None:
                raise ValidationError("The selected student does not exist.")
            cur.execute("SELECT user_id FROM users WHERE student_id = ?", (student_id,))
            if cur.fetchone() is not None:
                raise ValidationError("This student already has an account.")

        cur.execute(
            "INSERT INTO users (username, password_hash, role, student_id, must_change_password) "
            "VALUES (?, ?, ?, ?, ?)",
            (clean_username, _hash_password(clean_password), clean_role, student_id, int(bool(must_change_password))),
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
        cur.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?) ORDER BY user_id", (str(username).strip(),))
        user = cur.fetchone()

        if user is not None and user["locked_until"]:
            if datetime.fromisoformat(user["locked_until"]) > datetime.now():
                _verify_password(password, _dummy_hash())
                raise ValidationError(LOGIN_FAILED_MESSAGE)

        if user is None:
            _verify_password(password, _dummy_hash())
            raise ValidationError(LOGIN_FAILED_MESSAGE)
        if not _verify_password(password, user["password_hash"]):
            if user is not None:
                failures = user["failed_attempts"] + 1
                locked_until = None
                if failures >= MAX_FAILED_ATTEMPTS:
                    locked_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat(timespec="seconds")
                    failures = 0
                    log_audit("Auth", "Lockout", str(user["user_id"]), "Failure",
                               f"'{user['username']}' locked for {LOCKOUT_MINUTES} minutes after repeated failed logins.")
                cur.execute("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE user_id = ?",
                            (failures, locked_until, user["user_id"]))
                conn.commit()
            raise ValidationError(LOGIN_FAILED_MESSAGE)
        if user["failed_attempts"] or user["locked_until"]:
            cur.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE user_id = ?",
                        (user["user_id"],))
            conn.commit()
        if user["status"] != "Active":
            raise ValidationError("Your account is waiting for an administrator to approve it.")

        session.set_session(user["username"], user["role"], user["student_id"])
        log_audit("Auth", "Login", str(user["user_id"]), "Success",
                   f"'{user['username']}' logged in.")
        return {"user_id": user["user_id"], "username": user["username"],
                "role": user["role"], "student_id": user["student_id"],
                "must_change_password": bool(user["must_change_password"])}

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
            cur.execute("SELECT user_id, password_hash FROM users WHERE username = 'admin' AND must_change_password = 0")
            row = cur.fetchone()
            if row is not None and _verify_password(DEFAULT_ADMIN_PASSWORD, row["password_hash"]):
                cur.execute("UPDATE users SET must_change_password = 1 WHERE user_id = ?", (row["user_id"],))
                conn.commit()
            return
        cur.execute(
            "INSERT INTO users (username, password_hash, role, must_change_password) VALUES (?, ?, ?, 1)",
            ("admin", _hash_password(DEFAULT_ADMIN_PASSWORD), "Administrator"),
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
    session.require_roles(("Administrator",), "view accounts")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.username, u.role, u.status, u.created_at, u.student_id, s.name AS student_name
            FROM users u LEFT JOIN students s ON s.student_id = u.student_id
            ORDER BY u.user_id
        """)
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "list_users",
                   status="Open", message_reference=str(exc))
        return []
    finally:
        conn.close()


def change_password(user_id: int, new_password: str) -> None:
    session.require_roles(("Administrator",), "change passwords")
    user_id = validate_record_id(user_id, "Please select a valid user.")
    clean_password = validate_password(new_password)
    if clean_password in KNOWN_DEFAULT_PASSWORDS:
        raise ValidationError("Choose a password other than the default one.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise ValidationError("That user account does not exist.")
        cur.execute("UPDATE users SET password_hash = ?, must_change_password = 0 WHERE user_id = ?",
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


def change_own_password(current_password: str, new_password: str) -> None:
    """Any logged-in account changes its own password; the current password must be given."""
    if not session.is_logged_in():
        raise ValidationError("Log in first.")
    clean_password = validate_password(new_password)
    if clean_password in KNOWN_DEFAULT_PASSWORDS:
        raise ValidationError("Choose a password other than the default one.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE LOWER(username) = LOWER(?)",
                    (session.get_user(),))
        row = cur.fetchone()
        if row is None or not current_password or not _verify_password(current_password, row["password_hash"]):
            raise ValidationError("Your current password is not correct.")
        if current_password == clean_password:
            raise ValidationError("The new password must be different from the current one.")
        cur.execute("UPDATE users SET password_hash = ?, must_change_password = 0 WHERE user_id = ?",
                    (_hash_password(clean_password), row["user_id"]))
        conn.commit()
        log_audit("User", "ChangePassword", str(row["user_id"]), "Success",
                   f"'{session.get_user()}' changed their own password.")
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "change_own_password",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not change the password due to a database error.")
    finally:
        conn.close()


def flag_accounts_using_seed_password() -> int:
    """Make accounts that still use the shared demo password change it at next login. Returns how many."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE must_change_password = 0 AND role = 'Student'")
        ids = [r["user_id"] for r in cur.fetchall() if _verify_password(SEED_PASSWORD, r["password_hash"])]
        cur.executemany("UPDATE users SET must_change_password = 1 WHERE user_id = ?", [(i,) for i in ids])
        conn.commit()
        return len(ids)
    finally:
        conn.close()


def complete_forced_password_change(new_password: str) -> None:
    """The logged-in account replaces the default password it was forced to change."""
    if not session.is_logged_in():
        raise ValidationError("Log in first.")
    clean_password = validate_password(new_password)
    if clean_password in KNOWN_DEFAULT_PASSWORDS:
        raise ValidationError("Choose a password other than the default one.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, must_change_password FROM users WHERE LOWER(username) = LOWER(?)",
                    (session.get_user(),))
        row = cur.fetchone()
        if row is None or not row["must_change_password"]:
            raise ValidationError("This account is not waiting for a password change.")
        cur.execute("UPDATE users SET password_hash = ?, must_change_password = 0 WHERE user_id = ?",
                    (_hash_password(clean_password), row["user_id"]))
        conn.commit()
        log_audit("User", "ChangePassword", str(row["user_id"]), "Success",
                   f"'{session.get_user()}' replaced the default password.")
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "complete_forced_password_change",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not change the password due to a database error.")
    finally:
        conn.close()


def delete_user(user_id: int) -> None:
    session.require_roles(("Administrator",), "delete accounts")
    user_id = validate_record_id(user_id, "Please select a valid user.")
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


def register_student(username: str, password: str, registration_number: str, contact_number: str) -> int:
    """
    Self sign-up from the login screen. The registration number must belong to a student the
    hostel has already recorded, and the contact number must match the record. The account stays
    'Pending' until an Administrator approves it.
    """
    clean_username = validate_username(username)
    clean_password = validate_password(password)
    clean_reg = validate_registration_number(registration_number)
    clean_contact = validate_contact_number(contact_number)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT failures, locked_until FROM signup_attempts WHERE registration_number = ?", (clean_reg,))
        attempts = cur.fetchone()
        if attempts is not None and attempts["locked_until"] and \
                datetime.fromisoformat(attempts["locked_until"]) > datetime.now():
            raise ValidationError("Too many unsuccessful sign-up attempts for this registration number. "
                                  f"Try again in {SIGNUP_LOCKOUT_MINUTES} minutes or ask the hostel office.")
        cur.execute("SELECT student_id, contact_number FROM students WHERE UPPER(registration_number) = UPPER(?)", (clean_reg,))
        student = cur.fetchone()
        if student is None or student["contact_number"] != clean_contact:
            failures = (attempts["failures"] if attempts is not None else 0) + 1
            locked_until = None
            if failures >= MAX_SIGNUP_FAILURES:
                locked_until = (datetime.now() + timedelta(minutes=SIGNUP_LOCKOUT_MINUTES)).isoformat(timespec="seconds")
                failures = 0
            cur.execute("INSERT INTO signup_attempts (registration_number, failures, locked_until) VALUES (?, ?, ?) "
                        "ON CONFLICT(registration_number) DO UPDATE SET failures = excluded.failures, "
                        "locked_until = excluded.locked_until", (clean_reg, failures, locked_until))
            conn.commit()
            raise ValidationError("Registration number and contact number do not match a hostel record. "
                                  "Ask the hostel office to add or correct your details.")
        cur.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", (clean_username,))
        if cur.fetchone() is not None:
            raise ValidationError(f"Username '{clean_username}' is already taken.")
        cur.execute("SELECT user_id FROM users WHERE student_id = ?", (student["student_id"],))
        if cur.fetchone() is not None:
            raise ValidationError("This student already has an account.")
        cur.execute("INSERT INTO users (username, password_hash, role, student_id, status) "
                    "VALUES (?, ?, 'Student', ?, 'Pending')",
                    (clean_username, _hash_password(clean_password), student["student_id"]))
        cur.execute("DELETE FROM signup_attempts WHERE registration_number = ?", (clean_reg,))
        conn.commit()
        user_id = cur.lastrowid
        log_audit("User", "SignUp", str(user_id), "Success",
                   f"'{clean_username}' requested a student account (pending approval).")
        return user_id
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "register_student",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not create the account due to a database error.")
    finally:
        conn.close()


def approve_user(user_id: int) -> None:
    user_id = validate_record_id(user_id, "Please select a valid user.")
    if session.get_role() != "Administrator":
        raise ValidationError("Only an Administrator can approve accounts.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT username, status FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise ValidationError("That user account does not exist.")
        if row["status"] == "Active":
            raise ValidationError("That account is already active.")
        cur.execute("UPDATE users SET status = 'Active' WHERE user_id = ?", (user_id,))
        conn.commit()
        log_audit("User", "Approve", str(user_id), "Success", f"Approved account '{row['username']}'.")
    except ValidationError:
        raise
    except sqlite3.Error as exc:
        log_error("User", "DatabaseError", "High", "approve_user",
                   status="Open", message_reference=str(exc))
        raise ValidationError("Could not approve the account due to a database error.")
    finally:
        conn.close()
