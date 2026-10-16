# Commit Plan — BUG-011 fix (Batch 31)

```bash
git add app/utils/validation.py
git commit -m "fix: require ASCII identifiers for registration, room and username (BUG-011)" 
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-011" 
git push

git add docs/bugs/BUG-011.md BATCH31_COMMIT_PLAN.md
git commit -m "docs: add BUG-011 find-and-fix write-up" 
git push
```
