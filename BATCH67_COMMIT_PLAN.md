# Batch 67 – BUG-047 (off-disk backup copy)

```
git add app/database/backup.py
git commit -m "feat: copy each daily backup to HOSTEL_EXTRA_BACKUP_DIR when set (BUG-047)"

git add tests/test_backup.py
git commit -m "test: cover the extra backup folder and its failure logging (BUG-047)"

git add app/database/log_bugs.py docs/bugs/BUG-047.md BATCH67_COMMIT_PLAN.md BATCH67_HANDOFF_APPEND.md
git commit -m "docs: log and write up BUG-047"

git push
```

After pulling: `python -m app.database.log_bugs`
