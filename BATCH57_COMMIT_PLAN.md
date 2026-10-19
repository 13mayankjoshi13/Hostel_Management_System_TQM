# Batch 57 – BUG-037 (username enumeration)

```
git add app/services/auth_service.py
git commit -m "fix: make failed logins identical in message and timing for known, unknown and locked accounts (BUG-037)" 

git add tests/test_bug_fixes.py
git commit -m "test: cover username enumeration and update the lockout message check (BUG-037)"

git add app/database/log_bugs.py
git commit -m "docs: log BUG-037 in the bug tracker data"

git add docs/bugs/BUG-037.md BATCH57_COMMIT_PLAN.md
git commit -m "docs: write up BUG-037 (how found, root cause, fix, test)" 

git push
```

After pulling: `python -m app.database.log_bugs`.
