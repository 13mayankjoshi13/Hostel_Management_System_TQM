# Batch 60 – BUG-040 (window close handling)

```
git add app/screens/login_screen.py
git commit -m "fix: let the X button on the log-in window quit the application (BUG-040)" 

git add app/screens/main_window.py
git commit -m "fix: log the user out in the audit log when the main window is closed (BUG-040)" 

git add tests/test_close_ui.py
git commit -m "test: cover closing the log-in and main windows (BUG-040)" 

git add app/database/log_bugs.py docs/bugs/BUG-040.md BATCH60_COMMIT_PLAN.md
git commit -m "docs: log and write up BUG-040" 

git push
```

After pulling: `python -m app.database.log_bugs`.
