# Batch 58 – BUG-038 (sign-up guessing)

```
git add app/database/db.py
git commit -m "feat: add the signup_attempts table (BUG-038)" 

git add app/services/auth_service.py
git commit -m "fix: block a registration number for 15 minutes after 5 failed sign-ups (BUG-038)" 

git add tests/test_bug_fixes.py
git commit -m "test: cover sign-up throttling for known and unknown registration numbers (BUG-038)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-038 in the bug tracker data" 

git add docs/bugs/BUG-038.md BATCH58_COMMIT_PLAN.md
git commit -m "docs: write up BUG-038 (how found, root cause, fix, test)" 

git push
```

After pulling: `python -m app.database.log_bugs`. The new table is created automatically on start-up.
