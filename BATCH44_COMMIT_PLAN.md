# Batch 44 – BUG-024

```
git add app/services/allocation_service.py app/database/db.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-024.md BATCH44_COMMIT_PLAN.md
git commit -m "fix: make room allocation atomic so rooms cannot be overfilled (BUG-024)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-024.
