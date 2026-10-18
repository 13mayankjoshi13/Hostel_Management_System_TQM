# Batch 54 – BUG-034 (data health check)

```
git add app/database/check_data.py
git commit -m "feat: add a read-only check for existing bad data (BUG-034)" 

git add app/main.py
git commit -m "fix: run the data check at start-up and log what it finds (BUG-034)" 

git add tests/test_check_data.py tests/test_startup_errors.py
git commit -m "test: cover the data check and keep start-up tests off real data (BUG-034)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-034 in the bug tracker data" 
git add docs/bugs/BUG-034.md BATCH54_COMMIT_PLAN.md
git commit -m "docs: write up BUG-034 (how found, root cause, fix, test)"
git push
```

After pulling: `python -m app.database.log_bugs`, then `python -m app.database.check_data` once on your real database.
