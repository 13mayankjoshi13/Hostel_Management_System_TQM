# Batch 45 – BUG-025

```
git add app/services/auth_service.py app/database/db.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-025.md BATCH45_COMMIT_PLAN.md
git commit -m "fix: lock accounts after repeated failed logins (BUG-025)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-025. The new user columns are added automatically on start-up.
