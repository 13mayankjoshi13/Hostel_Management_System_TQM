# Batch 61 – BUG-041 (locked log files)

```
git add app/utils/logging_service.py
git commit -m "fix: queue log rows in a .pending file when the CSV is locked and add them later (BUG-041)"

git add tests/test_log_resilience.py tests/test_logging.py
git commit -m "test: cover locked log files and the pending queue (BUG-041)" 

git add app/database/log_bugs.py docs/bugs/BUG-041.md BATCH61_COMMIT_PLAN.md
git commit -m "docs: log and write up BUG-041" 

git push
```

After pulling: `python -m app.database.log_bugs`. Add `TQM/data/*.pending` to `.gitignore`.
