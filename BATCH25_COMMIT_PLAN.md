# Commit Plan — BUG-006 fix (Batch 25)

```bash
git add app/utils/validation.py
git commit -m "fix: limit leave length and date range (BUG-006)" 
git push

git add app/database/seed_demo.py tests/test_leave.py tests/test_student_portal.py
git commit -m "test: use dates relative to today in leave tests and demo data" 
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-006" 
git push

git add docs/bugs/BUG-006.md BATCH25_COMMIT_PLAN.md
git commit -m "docs: add BUG-006 find-and-fix write-up" 
git push
```
