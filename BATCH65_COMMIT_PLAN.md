# Batch 65 – BUG-045 (student ownership in leave and complaint services)

```
git add app/utils/session.py app/services/leave_service.py app/services/complaint_service.py
git commit -m "fix: students can only record leave, return and complaints for themselves (BUG-045)"

git add tests/test_bug_fixes.py
git commit -m "test: cover cross-student leave and complaint access (BUG-045)"

git add app/database/log_bugs.py docs/bugs/BUG-045.md BATCH65_COMMIT_PLAN.md BATCH65_HANDOFF_APPEND.md
git commit -m "docs: log BUG-045 and append BUG-044, BUG-045 to the handoff"

git push
```

After pulling: `python -m app.database.log_bugs`
