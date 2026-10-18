# Batch 38 – BUG-018

```
git add app/services/allocation_service.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-018.md BATCH38_COMMIT_PLAN.md
git commit -m "fix: close open leave when a room allocation is released (BUG-018)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-018.
