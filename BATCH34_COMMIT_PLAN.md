# Commit Plan — BUG-014 fix (Batch 34)

```bash
git add app/theme.py app/screens/complaint_screen.py app/screens/leave_screen.py app/screens/bug_screen.py
git commit -m "fix: keep the selected row after refresh on complaint, leave and bug screens (BUG-014)" 
git push

git add app/database/log_bugs.py tests/test_selection_ui.py
git commit -m "test: add UI regression tests and tracker entry for BUG-014" 
git push

git add docs/bugs/BUG-014.md BATCH34_COMMIT_PLAN.md
git commit -m "docs: add BUG-014 find-and-fix write-up" 
git push
```
