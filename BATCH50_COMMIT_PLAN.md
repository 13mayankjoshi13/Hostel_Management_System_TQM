# Batch 50 – BUG-030

```
git add app/utils/validation.py app/services/student_service.py app/services/auth_service.py app/database/db.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-030.md BATCH50_COMMIT_PLAN.md
git commit -m "fix: treat registration numbers case-insensitively (BUG-030)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-030.
