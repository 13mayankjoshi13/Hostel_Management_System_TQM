# Commit Plan — Authentication & Roles (Batch 9)

```bash
git add app/database/db.py
git commit -m "feat: add users table"
git push

git add app/utils/validation.py
git commit -m "feat: add username, password, and role validation"
git push

git add app/utils/session.py
git commit -m "feat: add runtime session module"
git push

git add app/utils/logging_service.py
git commit -m "refactor: logging reads the real logged-in user from session instead of a static constant"
git push

git add app/services/auth_service.py
git commit -m "feat: add authentication service (hashing, create user, login, logout, default admin bootstrap)"
git push

git add app/screens/login_screen.py app/screens/main_window.py app/main.py
git commit -m "feat: wire login gate into the app (splash -> login -> dashboard), add account info and Log out to sidebar"
git push

git add tests/test_auth.py
git commit -m "test: add module tests for authentication (Q09)"
git push

git add BATCH9_README.md BATCH9_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 9 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Database | `python -c "from app.database.db import initialize_database; initialize_database(); print('OK')"` |
| Validation | `python -m unittest tests.test_validation -v` |
| Session | `python -c "from app.utils import session; session.set_session('x','Staff'); print(session.get_user())"` |
| Logging | Log in as admin, perform any action, confirm `TQM/data/audit_logs.csv` shows `admin` not `system_admin` |
| Auth service | `python -m unittest tests.test_auth -v` |
| Login flow | `python run.py` — try a wrong password (generic error shows), then `admin` / `admin123`, confirm Dashboard opens and sidebar shows "admin · Administrator" |
| Logout | Click "Log out" — confirm it returns to the login screen, not a closed app |
| Full suite | `python -m unittest discover -s tests -v` — all 85 pass |

## Running Total

This batch contributes **8 commits**, bringing the project total to
**~57 commits**.

## Next

A user-management screen (create Warden/Staff accounts from the UI),
PDCA documentation, or a final documentation pass.
