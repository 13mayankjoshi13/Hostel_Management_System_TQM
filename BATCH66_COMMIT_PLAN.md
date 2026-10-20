# Batch 66 – BUG-046 (administrator password reset)

```
git add app/services/auth_service.py
git commit -m "fix: password reset clears the lockout and forces a new password (BUG-046)"

git add tests/test_bug_fixes.py
git commit -m "test: cover administrator password reset (BUG-046)"

git add app/database/log_bugs.py docs/bugs/BUG-046.md BATCH66_COMMIT_PLAN.md BATCH66_HANDOFF_APPEND.md
git commit -m "docs: log and write up BUG-046"

git push
```

After pulling: `python -m app.database.log_bugs`
