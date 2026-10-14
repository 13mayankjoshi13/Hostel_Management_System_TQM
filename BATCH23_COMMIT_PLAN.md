# Commit Plan — BUG-004 fix (Batch 23)

```bash
git add app/utils/validation.py
git commit -m "fix: reject non-whole room capacity such as 1.5 and True (BUG-004)"
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-004" 
git push

git add docs/bugs/BUG-004.md BATCH23_COMMIT_PLAN.md
git commit -m "docs: add BUG-004 find-and-fix write-up"
git push
```
