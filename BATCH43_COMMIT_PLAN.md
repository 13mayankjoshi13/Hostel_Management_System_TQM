# Batch 43 – BUG-023

```
git add app/utils/session.py app/services/ app/database/log_bugs.py tests/test_bug_fixes.py tests/test_requests_batch.py docs/bugs/BUG-023.md BATCH43_COMMIT_PLAN.md
git commit -m "fix: enforce roles in services, not only navigation (BUG-023)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-023.
