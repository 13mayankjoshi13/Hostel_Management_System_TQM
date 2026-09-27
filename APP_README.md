# Application Foundation — Batch 1

This batch adds the first working software layer on top of the TQM
documentation foundation. It is intentionally scoped to **Student
Management** and **Room Management** only — enough to prove the whole
pipeline (UI → Validation → Service → Database → Logging) end-to-end
before Room Allocation, Complaints, and the Bug Tracker are layered on
in later batches.

## What This Batch Delivers

| Area | What's implemented |
|---|---|
| Database | SQLite schema for `students`, `rooms`, and a forward-looking `allocations` table |
| Strict Validation (Q09) | `app/utils/validation.py` — name, registration number, contact number, room number, room type, capacity, all rejecting bad input before it reaches the database |
| Exception Handling (Q09) | `app/utils/exception_handler.py` — central handler; no unexpected exception reaches the user as a raw traceback |
| Error Logs (Q09) | `app/utils/logging_service.py` writes real rows to `TQM/data/error_logs.csv` whenever a database error or unexpected exception occurs |
| Audit Logs | Every successful create/delete writes a real row to `TQM/data/audit_logs.csv` |
| Module Tests (Q09) | `tests/test_validation.py` — 17 positive/negative cases across validation rules and duplicate-prevention rules |
| GUI | Tkinter window with Students and Rooms tabs (add + list) |

## What Is Intentionally NOT in This Batch

- Room Allocation logic (table exists, service does not yet — next batch)
- Complaint Management
- Bug Tracker (defect_log.csv stays empty until real defects are found and triaged)
- Authentication / user roles (a placeholder `CURRENT_USER` / `CURRENT_ROLE` is used in `app/config.py`)
- Quality Monitoring dashboards / Pareto / Fishbone automation

These follow in the order given in `FULL PROJECT CONTEXT` section 24.

## How to Install These Files

1. Extract this ZIP.
2. Copy `run.py`, `requirements.txt`, `app/`, and `tests/` into the root
   of your `Project Guidelines/` VS Code folder (alongside your existing
   `docs/` and `TQM/` folders).
3. Do not overwrite `docs/` or `TQM/` — this batch does not touch them.

## How to Run

```bash
python run.py
```

The first run creates `app/database/hostel.db` automatically (empty —
no seed data, per the "do not fabricate quality results" rule).

## How to Test

```bash
python -m unittest discover -s tests -v
```

Expected: all tests pass. This is real evidence for
`TQM/quality_features.md` → Module Tests, not a placeholder claim.

## How to Generate Real Quality Evidence

- Trigger a validation failure in the UI (e.g. leave the name blank and
  click "Add Student") → confirms strict validation is live; no CSV
  entry is expected here, since a *rejected* input is prevention working
  correctly, not an error.
- Add a student successfully → open `TQM/data/audit_logs.csv` and
  confirm a new row appeared with `action = Create`.
- To generate a real error-log row for demonstration purposes, you can
  temporarily rename `app/database/hostel.db` while the app is running
  and attempt an action — the resulting `sqlite3.Error` will be caught
  and logged with a real timestamp and error_id.

## Known Limitations (for `PROJECT_STATUS.md` — not yet updated here)

- No GUI field for deleting is wired in yet (`delete_student` /
  `delete_room` exist in the service layer and are covered indirectly by
  future tests, but no button calls them yet).
- Single hard-coded `CURRENT_USER` until authentication exists — audit
  and error logs will show `system_admin` for every row until then.
