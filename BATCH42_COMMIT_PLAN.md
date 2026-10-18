# Batch 42 – BUG-022

```
git add app/utils/validation.py app/services/event_service.py app/database/log_bugs.py tests/test_bug_fixes.py docs/bugs/BUG-022.md BATCH42_COMMIT_PLAN.md
git commit -m "fix: normalise event titles and ignore case in duplicate check (BUG-022)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-022.
