# Batch 10 — User Management

Administrator-only screen to manage accounts.

- `auth_service`: `list_users`, `change_password`, `delete_user`
- Guards (checked before any write): cannot delete your own logged-in account; cannot delete the last Administrator.
- `screens/user_screen.py`: create account, change password, delete account.
- Sidebar: "User Management" appears only for Administrators; `show_screen` also blocks other roles.
- Every action is audit-logged. Password hashes are never returned to the UI.

## Tests
`python -m unittest discover -s tests -t .` → 93 passed (8 new in `tests/test_auth.py`).

## Not verified
UI not screenshot-checked this batch (no tkinter in the build environment). Open the app, log in as `admin`/`admin123`, and check the User Management screen and a Warden login (menu item hidden).
