# Batch 37 – BUG-017

```
git add app/utils/validation.py app/services/complaint_service.py app/services/leave_service.py app/services/allocation_service.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-017.md BATCH37_COMMIT_PLAN.md
git commit -m "fix: reject bool and fractional record IDs (BUG-017)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-017.
