# Commit Plan — BUG-008 fix (Batch 27)

```bash
git add app/services/allocation_service.py
git commit -m "fix: sort allotment export rooms in natural order (BUG-008)" 
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression test and tracker entry for BUG-008" 
git push

git add docs/bugs/BUG-008.md BATCH27_COMMIT_PLAN.md
git commit -m "docs: add BUG-008 find-and-fix write-up" 
git push
```
