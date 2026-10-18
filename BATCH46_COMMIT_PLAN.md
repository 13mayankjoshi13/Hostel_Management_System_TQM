# Batch 46 – BUG-026

```
git add app/utils/exception_handler.py app/screens/main_window.py app/database/log_bugs.py tests/test_callback_errors_ui.py docs/bugs/BUG-026.md BATCH46_COMMIT_PLAN.md
git commit -m "fix: log and report exceptions raised inside Tk callbacks (BUG-026)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-026.
