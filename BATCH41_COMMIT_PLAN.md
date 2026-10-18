# Batch 41 – BUG-021

```
git add app/utils/validation.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-021.md BATCH41_COMMIT_PLAN.md
git commit -m "fix: limit calendar event dates to a 5-year window (BUG-021)"
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-021.
