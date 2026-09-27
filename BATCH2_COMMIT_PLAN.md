# Commit Plan — Room Allocation (Batch 2)

```bash
git add app/services/allocation_service.py
git commit -m "feat: add room allocation service with full prevention pipeline"
git push

git add app/ui/main_window.py
git commit -m "feat: add Room Allocation tab to GUI"
git push

git add tests/test_allocation.py
git commit -m "test: add module tests for room allocation (Q09)"
git push

git add BATCH2_README.md BATCH2_COMMIT_PLAN.md
git commit -m "docs: add batch 2 README and commit plan"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Allocation service | `python -m unittest tests.test_allocation -v` |
| GUI | `python run.py` — add a student, add a room, allocate, confirm it appears in "Active Allocations", release it, confirm it disappears |
| Tests | `python -m unittest discover -s tests -v` — all 31 pass |
| Audit evidence | After allocating/releasing via the GUI (not tests), open `TQM/data/audit_logs.csv` and confirm new `Allocation` rows appeared |

## Running Total

This batch contributes **4 commits**, bringing the project total to
**11 commits** across the documentation foundation, Batch 1, and Batch 2.

## Next Batch

**Complaint Management** — create, assign, track status, resolve with
timestamp, audit history. The `allocations` table from this batch means
a complaint can optionally reference the student's current room.
