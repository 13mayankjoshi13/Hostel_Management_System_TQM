# Batch 73 – Windows CI fixes (BUG-051)

First remove the old duplicate workflow ("Build & Release Executable") if you have not yet:
```
git rm .github/workflows/android-release.yml
git commit -m "ci: remove the old duplicate release workflow"
```

```
git add app/database/db.py
git commit -m "fix: always close the database connection when schema setup fails (BUG-051)"

git add tests/test_startup_errors.py tests/test_timestamps.py
git commit -m "test: cover closing on failure; skip time-zone tests where tzset is missing (BUG-051)"

git add docs/Q09_final_submission.md app/database/log_bugs.py docs/bugs/BUG-051.md BATCH73_COMMIT_PLAN.md BATCH73_HANDOFF_APPEND.md
git commit -m "docs: log and write up BUG-051"

git push
```

Then run the release again. If you already pushed the tag, delete and re-push it on the new commit:
```
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
git tag v1.0.0
git push origin v1.0.0
```
After pulling: `python -m app.database.log_bugs`, then append `BATCH73_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
