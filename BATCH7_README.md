# Batch 7 — Bug Tracker (Q09 Feature #4)

The last unbuilt Q09 feature. All five are now implemented: Exception
Handling, Strict Validation, Module Tests, Bug Tracker, Error Logs.

## Status Pipeline

```
Open --start_progress--> In Progress --mark_fixed--> Fixed --close_bug--> Closed
```

Forward-only, same prevention-at-source pattern as allocations and
complaints — can't skip steps, can't go backward, and **"Fixed" requires
a documented root cause, corrective action, and test case reference**
before it's accepted. You cannot mark something fixed without saying
how, which directly ties the Bug Tracker to the FMEA/root-cause-analysis
side of the TQM plan rather than being a bare status field.

## Fields (exactly matching the assigned spec)

Bug ID, Date, Module, Category, Title, Description, Severity, Priority,
Status, Root Cause, Corrective Action, Test Case.

## What's New

| File | Purpose |
|---|---|
| `app/services/bug_service.py` | `log_bug()`, `start_progress()`, `mark_fixed()`, `close_bug()`, `get_all_bugs()` |
| `app/database/db.py` (updated) | New `bugs` table |
| `app/utils/validation.py` (updated) | Module, category, title, description, severity, priority, root cause, corrective action, test case validators |
| `app/utils/logging_service.py` (updated) | `log_defect()` — writes real rows to `TQM/data/defect_log.csv` |
| `app/screens/bug_screen.py` | **New screen** — log a bug, work it through the pipeline via the table's action buttons |
| `app/screens/main_window.py` (updated) | "Bug Tracker" added to the sidebar |
| `app/screens/dashboard_screen.py` (updated) | New "Open Bugs" stat — directly reflects the assigned quality goal (Q09: Reduce Bugs) |
| `tests/test_bug.py` | 17 new tests |

## Why defect_log.csv Is Append-Only

Same pattern as `error_logs.csv` and `audit_logs.csv`: every call to
`log_defect()` writes a **new** row reflecting the bug's state at that
moment, rather than overwriting a single row in place. So the CSV ends
up holding the bug's full history — creation, then every status
change — which is exactly the shape of data Pareto/Fishbone/PDCA
analysis will need later. Nothing here is fabricated: a bug only gets a
"Fixed" row once you've actually entered a root cause, corrective
action, and test case through the UI.

## Verified End-to-End

Logged two real bugs, ran one through the full
Open → In Progress → Fixed → Closed pipeline, and confirmed via
screenshot that: the table's status color updates at each step, the
Dashboard's "Open Bugs" count updates correctly (only counts Open/In
Progress), and the Dashboard's "Recent Activity" panel shows the full
audit trail of the bug's lifecycle events — real evidence, not a mockup.

## How to Install

**Replace:** `app/database/db.py`, `app/utils/validation.py`,
`app/utils/logging_service.py`, `app/screens/main_window.py`,
`app/screens/dashboard_screen.py`.
**Add:** `app/services/bug_service.py`, `app/screens/bug_screen.py`,
`tests/test_bug.py`.

## How to Run / Test

```bash
python run.py
python -m unittest discover -s tests -v   # expect 62 passed
```

## What's Left on the Original Roadmap

All five Q09 features are now built. What remains is analysis/reporting
layered on top of the real data this app has been generating since
Batch 1: **Quality Monitoring** dashboards, and **SQC automation**
(Pareto chart + Fishbone diagram generated from `defect_log.csv`, PDCA
cycle documentation tied to real recurring issues) — plus a final
documentation pass replacing "planned/pending" placeholders in
`docs/testing.md` and `TQM/requirements_traceability.md` with real
results once you've used the app enough to have real data.
