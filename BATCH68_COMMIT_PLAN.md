# Batch 68 – BUG-048 (Hindi names and Excel export)

```
git add app/utils/validation.py
git commit -m "fix: accept Devanagari and other combining-mark names, normalise to NFC (BUG-048)"

git add app/services/allocation_service.py tests/test_leave.py
git commit -m "fix: write the allotment CSV with a BOM so Excel reads non-English names (BUG-048)"

git add tests/test_bug_fixes.py
git commit -m "test: cover Devanagari names and the export encoding (BUG-048)"

git add app/database/log_bugs.py docs/bugs/BUG-048.md BATCH68_COMMIT_PLAN.md BATCH68_HANDOFF_APPEND.md
git commit -m "docs: log and write up BUG-048"

git push
```

After pulling: `python -m app.database.log_bugs`
