# Batch 52 – BUG-032 (change own password)

```
git add app/services/auth_service.py
git commit -m "feat: add change_own_password requiring the current password (BUG-032)"

git add app/screens/main_window.py
git commit -m "feat: add a Change password link to the sidebar for every role (BUG-032)" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" 

git add tests/test_bug_fixes.py
git commit -m "test: cover changing your own password (BUG-032)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-032 in the bug tracker data" 

git add docs/bugs/BUG-032.md BATCH52_COMMIT_PLAN.md
git commit -m "docs: write up BUG-032 (how found, root cause, fix, test)" 

git push
```

After pulling: `python -m app.database.log_bugs`.
