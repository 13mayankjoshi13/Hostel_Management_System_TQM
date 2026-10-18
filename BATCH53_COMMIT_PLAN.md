# Batch 53 – BUG-033 (idle log-out)

```
git add app/utils/idle.py app/config.py
git commit -m "feat: add an inactivity tracker and a 15-minute idle timeout setting (BUG-033)" 

git add app/screens/main_window.py
git commit -m "fix: log out an idle session and cancel the clock timer on close (BUG-033)" 

git add tests/test_idle.py
git commit -m "test: cover the idle tracker and idle log-out (BUG-033)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-033 in the bug tracker data" 

git add docs/bugs/BUG-033.md BATCH53_COMMIT_PLAN.md
git commit -m "docs: write up BUG-033 (how found, root cause, fix, test)" 

git push
```

After pulling: `python -m app.database.log_bugs`.
