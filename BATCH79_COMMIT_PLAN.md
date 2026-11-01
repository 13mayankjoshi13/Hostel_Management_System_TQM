# Batch 79 – Settings, dark/light theme, accent colour

```
git add app/theme.py app/screens/login_screen.py app/screens/splash_screen.py app/screens/student_home_screen.py
git commit -m "feat: light and dark palettes with a changeable accent colour"

git add app/database/db.py app/services/settings_service.py
git commit -m "feat: save appearance per user"

git add app/services/audit_service.py
git commit -m "feat: audit log viewer and student data download for administrators"

git add app/screens/settings_screen.py app/screens/main_window.py app/screens/dashboard_screen.py
git commit -m "feat: Settings screen with Quality Monitoring inside; live theme switch; scrolling sidebar"

git add tests/test_settings.py tests/test_settings_ui.py tests/test_roles.py
git commit -m "test: cover settings, appearance validation, audit viewer and theme switching"

git add docs/ROLES.md BATCH79_COMMIT_PLAN.md BATCH79_HANDOFF_APPEND.md
git commit -m "docs: Batch 79 handoff"

git push
```

Apply after Batch 78. After pulling, append `BATCH79_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
