# Batch 76 – Super Admin role, role-specific menus and four login panels

```
git add app/utils/session.py app/utils/validation.py app/config.py
git commit -m "feat: Super Admin role and role groups (admin, warden, staff)"

git add app/services/auth_service.py
git commit -m "feat: only a Super Admin manages admin accounts; default account is Super Admin; promote first admin on old databases"

git add app/services/room_service.py app/services/student_service.py app/services/allocation_service.py app/services/fine_service.py app/services/bug_service.py app/services/worker_service.py app/services/event_service.py
git commit -m "feat: enforce per-role permissions in the services"

git add app/screens/login_screen.py app/screens/main_window.py app/screens/user_screen.py app/screens/dashboard_screen.py app/screens/calendar_screen.py
git commit -m "feat: Student, Staff, Admin and Super Admin login tabs and a menu per role"

git add tests/test_roles.py tests/test_auth.py tests/test_login_panels.py tests/test_fine_worker_screens_ui.py
git commit -m "test: cover the role matrix, admin account rules and login panels"

git add docs/ROLES.md BATCH76_COMMIT_PLAN.md BATCH76_HANDOFF_APPEND.md
git commit -m "docs: roles table and handoff update"

git push
```

Apply after Batches 74 and 75. After pulling, append `BATCH76_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
