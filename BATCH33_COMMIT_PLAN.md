# Commit Plan — BUG-013 fix (Batch 33)

```bash
git add app/screens/allocation_screen.py
git commit -m "fix: offer only free students and rooms with space on the allocation screen (BUG-013)" 
git push

git add app/database/log_bugs.py tests/test_allocation_screen_ui.py
git commit -m "test: add UI regression tests and tracker entry for BUG-013" 
git push

git add docs/bugs/BUG-013.md BATCH33_COMMIT_PLAN.md
git commit -m "docs: add BUG-013 find-and-fix write-up" 
git push
```
