# Commit Plan — BUG-002 fix (Batch 21)

```bash
git add app/utils/validation.py
git commit -m "fix: require valid Indian mobile format for contact number (BUG-002)" 
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-002" 
git push

git add docs/bugs/BUG-002.md BATCH21_COMMIT_PLAN.md
git commit -m "docs: add BUG-002 find-and-fix write-up" 
git push
```
