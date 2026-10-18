# Batch 48 – BUG-028

```
git add app/services/auth_service.py app/database/db.py app/screens/main_window.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-028.md BATCH48_COMMIT_PLAN.md
git commit -m "fix: force the default admin to change its password (BUG-028)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-028. The new user column is added automatically on start-up.
