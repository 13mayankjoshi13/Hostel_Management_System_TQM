# Batch 63 – BUG-043 (backup restore and partial backups)

```
git add app/database/backup.py
git commit -m "fix: refuse to restore non-hostel databases and clean up failed backups (BUG-043)" 

git add tests/test_backup.py
git commit -m "test: cover foreign database restore and failed backup cleanup (BUG-043)" 

git add app/database/log_bugs.py docs/bugs/BUG-043.md BATCH63_COMMIT_PLAN.md BATCH63_HANDOFF_APPEND.md
git commit -m "docs: log BUG-043 and append BUG-036 to BUG-043 to the handoff" 
git push
```

After pulling: `python -m app.database.log_bugs`, then append `BATCH63_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
