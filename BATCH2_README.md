# Batch 2 — Room Allocation

Adds the Room Allocation module on top of Batch 1 (Students, Rooms). This
is the feature the project's TQM plan uses as the worked example for
Error Prevention at Source (section 6):

```
Select Student
     |
Check Student (exists)
     |
Select Room
     |
Check Room Exists
     |
Check Capacity (active allocations < room capacity)
     |
Check Existing Allocation (student not already actively allocated)
     |
Allocate
     |
Audit the action
```

## What's New

| File | Purpose |
|---|---|
| `app/services/allocation_service.py` | The full prevention pipeline above, plus `release_allocation()` and `get_active_allocations()` |
| `app/ui/main_window.py` (updated) | New "Room Allocation" tab — dropdowns for student/room, active-allocation list, Allocate/Release buttons |
| `tests/test_allocation.py` | 9 new tests: successful allocation, nonexistent student/room, capacity exceeded, duplicate active allocation, double-room allows two allocations, release frees the room, release edge cases |

Total test count is now **31** (22 from Batch 1 + 9 new).

## Design Notes

- **Capacity check** counts only `status = 'Active'` allocations against
  the room's `capacity`, so releasing an allocation immediately frees a
  slot for reallocation — verified by `test_release_allocation_frees_room`.
- **Duplicate allocation check** is per student, not per room: a student
  can't hold two active allocations at once, matching the "Prevent
  Duplicate Allocation" requirement in section 15.
- **Release, not delete**: an allocation's row is kept with
  `status = 'Released'` rather than deleted, so allocation history stays
  in the database for future reporting/traceability — this satisfies the
  "Traceability" customer requirement in section 5 without needing a
  separate history table yet.
- Every successful allocate/release writes a real row to
  `TQM/data/audit_logs.csv` when you run the app (not during tests — see
  the note below).

## A Note on the Test Fix from Batch 1

`tests/test_allocation.py` follows the same temp-file isolation pattern
already applied to `tests/test_validation.py` (temp SQLite DB, temp
error/audit CSVs) — this batch does **not** write to your real
`TQM/data/*.csv` files when you run the test suite.

## How to Install

1. Extract this ZIP.
2. Copy `app/services/allocation_service.py` into your existing
   `app/services/` folder.
3. **Replace** your existing `app/ui/main_window.py` with the one in this
   ZIP (it now includes the Allocation tab; everything from Batch 1 is
   preserved plus the addition).
4. Copy `tests/test_allocation.py` into your existing `tests/` folder.
5. Nothing else needs to change — `run.py`, `requirements.txt`, and the
   rest of `app/` are unchanged from Batch 1 (included here only so the
   ZIP is self-contained if you want to diff against it).

## How to Run

```bash
python run.py
```

Add at least one student and one room first (Students / Rooms tabs),
then switch to "Room Allocation" — the dropdowns refresh automatically
whenever you open that tab.

## How to Test

```bash
python -m unittest discover -s tests -v
```

Expected: **31 passed**.
