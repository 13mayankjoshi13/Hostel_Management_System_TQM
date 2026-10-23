# Batch 72 – BUG-050 and the Windows release workflow

```
git add app/config.py
git commit -m "fix: keep data in the user profile when running as a packaged exe (BUG-050)"

git add tests/test_packaged_paths.py
git commit -m "test: cover packaged-exe data paths (BUG-050)"
                
git rm .github/workflows/android-release.yml
git add .github/workflows/release-exe.yml
git commit -m "ci: rename the release workflow, run tests before building the exe"

git add docs/Q09_final_submission.md app/database/log_bugs.py docs/bugs/BUG-050.md BATCH72_COMMIT_PLAN.md BATCH72_HANDOFF_APPEND.md
git commit -m "docs: log and write up BUG-050"

git push
```

## Making the release
```
git tag v1.0.0
git push origin v1.0.0
```
GitHub Actions runs the tests, builds `HostelManagementSystem.exe` and attaches it to a new Release (Repository → Actions to watch; Releases to download). The `exe` is also kept as a build artifact. You can also run the workflow by hand from the Actions tab (no release is created that way).

First run on Windows: SmartScreen may warn "Windows protected your PC" because the exe is unsigned; choose More info → Run anyway.
After pulling: `python -m app.database.log_bugs`, then append `BATCH72_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
