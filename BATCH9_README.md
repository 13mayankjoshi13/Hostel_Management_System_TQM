# Batch 9 — Authentication & Roles

Replaces the hard-coded `system_admin` in every log entry with the
actual logged-in user. Roles match the stakeholders your own project
spec already names: **Administrator**, **Warden**, **Staff**.

## Flow

```
Splash (brief) -> Login (modal, required) -> Dashboard
```

The main window stays hidden until `authenticate()` succeeds. Every
screen's sidebar footer shows who's logged in and a **Log out** link
that clears the session and returns to the login screen (not the OS
window-close button — closing the login window is disabled on purpose,
since the app isn't usable without a session).

## Security Notes

- Passwords are **never stored in plain text**: PBKDF2-HMAC-SHA256,
  100,000 iterations, a random 16-byte salt per user. Standard-library
  only (`hashlib`) — no new dependency.
- Login failure shows one generic message ("Invalid username or
  password") regardless of whether the username or the password was
  wrong — standard practice so a failed attempt can't be used to
  enumerate valid usernames.
- **First-run default account:** `admin` / `admin123`, created
  automatically the first time the app runs if no accounts exist yet
  (`ensure_default_admin()` in `auth_service.py`). Shown on the login
  screen itself as a reminder. There's no "create user" screen yet (see
  below) — change this password by calling `auth_service.create_user()`
  directly for now, or wait for a user-management screen in a future
  batch.

## What's New

| File | Purpose |
|---|---|
| `app/database/db.py` (updated) | New `users` table |
| `app/utils/validation.py` (updated) | `validate_username`, `validate_password`, `validate_role` |
| `app/utils/session.py` | **New** — runtime-mutable "who's logged in right now," read by logging at call time |
| `app/utils/logging_service.py` (updated) | Now reads `session.get_user()` / `session.get_role()` instead of the static `CURRENT_USER` constant |
| `app/services/auth_service.py` | **New** — `create_user()`, `authenticate()`, `logout()`, `ensure_default_admin()` |
| `app/screens/login_screen.py` | **New** — modal login form |
| `app/screens/main_window.py` (updated) | Wires splash → login → dashboard; sidebar account block + Log out |
| `app/main.py` (updated) | Calls `ensure_default_admin()` after database init |
| `tests/test_auth.py` | 16 new tests |

## A Bug I Caught and Fixed While Verifying This

Same class of issue as the splash-screen sizing bug from Batch 6: the
login window's first size (380×300) clipped both the title text and the
bottom of the form. Caught via the same virtual-display screenshot
process used for every UI batch, fixed by enlarging the window
(440×380) — confirmed clean afterward with a full login → wrong
password → correct password → navigate → logout cycle, screenshotted
at every step.

## How to Install

**Replace:** `app/database/db.py`, `app/utils/validation.py`,
`app/utils/logging_service.py`, `app/screens/main_window.py`,
`app/main.py`.
**Add:** `app/utils/session.py`, `app/services/auth_service.py`,
`app/screens/login_screen.py`, `tests/test_auth.py`.

## How to Run / Test

```bash
python run.py        # log in with admin / admin123 on first run
python -m unittest discover -s tests -v   # expect 85 passed
```

## What's Left

- A **user-management screen** (create Warden/Staff accounts, change
  the default admin password) — right now `create_user()` only exists
  in the service layer with no UI.
- PDCA documentation, final documentation pass (unchanged from Batch 8).
