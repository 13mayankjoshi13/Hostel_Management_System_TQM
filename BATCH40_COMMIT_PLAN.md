# Batch 40 – BUG-020

```
git add app/utils/logging_service.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-020.md BATCH40_COMMIT_PLAN.md
git commit -m "fix: neutralise formula text in evidence log CSVs (BUG-020)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-020.
