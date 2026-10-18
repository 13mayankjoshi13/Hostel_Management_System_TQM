# Batch 49 – BUG-029

```
git add app/services/auth_service.py app/database/seed_demo.py app/database/log_bugs.py tests/test_bug_fixes.py tests/test_seed_demo.py docs/bugs/BUG-029.md BATCH49_COMMIT_PLAN.md
git commit -m "fix: force seeded student accounts to replace the shared password (BUG-029)" 
git push
```

After pulling: `python -m app.database.log_bugs` to load BUG-029, then re-run `python -m app.database.seed_demo --real` once so accounts already created are flagged.
