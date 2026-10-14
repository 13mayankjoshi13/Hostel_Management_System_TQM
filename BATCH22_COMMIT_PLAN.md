# Commit Plan — BUG-003 fix (Batch 22)

```bash
git add app/utils/validation.py app/services/room_service.py
git commit -m "fix: treat room numbers case-insensitively (BUG-003)" 

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-003" 
git push

git add docs/bugs/BUG-003.md BATCH22_COMMIT_PLAN.md
git commit -m "docs: add BUG-003 find-and-fix write-up" 
git push
```
