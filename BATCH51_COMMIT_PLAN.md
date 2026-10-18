# Batch 51 – BUG-031 (backup and restore)

Small commits, in this order:

```
git add app/database/backup.py
git commit -m "feat: add daily verified database backup with pruning and restore"

git add app/main.py
git commit -m "fix: take a database backup at start-up and mention restore in the start-up error (BUG-031)"

git add tests/test_backup.py tests/test_startup_errors.py
git commit -m "test: cover backup, pruning, damaged-file handling and restore (BUG-031)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-031 in the bug tracker data" 

git add docs/bugs/BUG-031.md BATCH51_COMMIT_PLAN.md
git commit -m "docs: write up BUG-031 (how found, root cause, fix, test)" 

git push
```

Add `app/database/backups/` and `app/database/hostel.db` to `.gitignore` (they hold real student data). After pulling: `python -m app.database.log_bugs`.
