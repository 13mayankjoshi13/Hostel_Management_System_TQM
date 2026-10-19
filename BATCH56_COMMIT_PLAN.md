# Batch 56 – BUG-036 (student read access)

```
git add app/services/complaint_service.py app/services/leave_service.py app/services/allocation_service.py app/services/bug_service.py
git commit -m "fix: require a staff role to list complaints, leaves, allocations, bugs and the allotment export (BUG-036)" 

git add tests/test_bug_fixes.py
git commit -m "test: cover student access to other people's records (BUG-036)" 

git add app/database/log_bugs.py
git commit -m "docs: log BUG-036 in the bug tracker data" 

git add docs/bugs/BUG-036.md BATCH56_COMMIT_PLAN.md
git commit -m "docs: write up BUG-036 (how found, root cause, fix, test)" 
git push
```

After pulling: `python -m app.database.log_bugs`.
