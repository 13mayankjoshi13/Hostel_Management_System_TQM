# Batch 59 – BUG-039 (UTC vs local times)

```
git add app/utils/timefmt.py
git commit -m "feat: add UTC storage and local display helpers for timestamps (BUG-039)" 

git add app/services/complaint_service.py app/services/allocation_service.py app/services/leave_service.py app/services/auth_service.py app/services/student_portal_service.py
git commit -m "fix: store resolved/returned times in UTC and show local times on screens and export (BUG-039)"

git add app/database/db.py
git commit -m "fix: convert older local resolved/returned times to UTC once at start-up (BUG-039)" 

git add tests/test_timestamps.py
git commit -m "test: cover UTC storage, local display and the one-time conversion (BUG-039)" 

git add app/database/log_bugs.py docs/bugs/BUG-039.md BATCH59_COMMIT_PLAN.md
git commit -m "docs: log and write up BUG-039" 

git push
```

After pulling: `python -m app.database.log_bugs`.
