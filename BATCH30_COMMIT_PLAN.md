# Commit Plan — BUG-010 fix (Batch 30)

```bash
git add app/utils/validation.py
git commit -m "fix: normalise student name whitespace and require a letter (BUG-010)" 
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-010" 
git push

git add docs/bugs/BUG-010.md BATCH30_COMMIT_PLAN.md
git commit -m "docs: add BUG-010 find-and-fix write-up" 
git push
```
