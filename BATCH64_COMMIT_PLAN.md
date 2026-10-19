# Batch 64 – BUG-044 (names and CSV export)

```
git add app/utils/validation.py
git commit -m "fix: student names must start with a letter (BUG-044)" 
git add app/services/allocation_service.py
git commit -m "fix: neutralise formula text in the allotment CSV export (BUG-044)" 

git add tests/test_bug_fixes.py
git commit -m "test: cover name rule and export neutralising (BUG-044)" 

git add app/database/log_bugs.py docs/bugs/BUG-044.md BATCH64_COMMIT_PLAN.md
git commit -m "docs: log and write up BUG-044" 

git push
```

After pulling: `python -m app.database.log_bugs`.
