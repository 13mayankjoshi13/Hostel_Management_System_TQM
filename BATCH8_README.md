# Batch 8 — Quality Monitoring + SQC Automation

Pareto chart and Fishbone diagram generated live from real Bug Tracker
data — no sample/placeholder numbers anywhere. With zero bugs logged,
both charts show an honest "not enough data yet" state instead of
fabricating an example, matching the project's "do not fabricate
quality results" rule.

## What's New

| File | Purpose |
|---|---|
| `app/services/quality_service.py` | Pure read-only analysis: `get_quality_summary()`, `get_pareto_data()`, `get_fishbone_data()` |
| `app/screens/quality_screen.py` | **New screen** — KPI strip + Canvas-drawn Pareto chart + Canvas-drawn Fishbone diagram |
| `app/screens/main_window.py` (updated) | "Quality Monitoring" added to the sidebar; window enlarged to fit both charts without clipping |
| `app/screens/dashboard_screen.py` | unchanged this batch |
| `tests/test_quality.py` | 7 new tests (including the empty-data path) |

No new third-party dependency: both charts are drawn directly on a
plain `tk.Canvas`, so `requirements.txt` still needs nothing beyond the
standard library.

## Pareto Chart

Bug counts grouped by **Category** (Functional, UI/UX, Validation,
Performance, Data Integrity, Security, Other), sorted descending, with
the standard cumulative-percentage line overlaid — the classic 80/20
defect-concentration view, built from whatever categories you've
actually used when logging bugs.

## Fishbone (Cause-and-Effect) Diagram

Uses the exact six branches from your course material — People,
Process, Software/Code, Database, Infrastructure, Measurement — with
real bug titles plotted as causes under the right branch. Since a bug's
logged **Category** doesn't map 1:1 onto those six branches, the
mapping is explicit and documented in `quality_service.py`
(`CATEGORY_TO_FISHBONE`):

| Bug Category | Fishbone Branch |
|---|---|
| Functional | Process |
| UI/UX | People |
| Validation, Security | Software/Code |
| Performance | Infrastructure |
| Data Integrity | Database |
| Other | Measurement |

This is a judgment call, not something the course specified — worth
mentioning if asked about it in your viva, and easy to change in one
place if you'd map it differently.

## Two Real Bugs I Fixed While Verifying This

Visual verification (same virtual-display process as every UI batch)
caught two real problems before shipping:

1. **Window too short** — with a KPI strip plus two chart panels
   stacked, the old 1100×700 default window clipped the bottom of the
   Fishbone diagram. Fixed by enlarging the default window and trimming
   chart heights slightly. This is the same class of bug noted in
   `AI_CONTEXT_HANDOFF.md` from Batch 5 — worth double-checking on any
   future screen that stacks more than two sections.
2. **A fallback-size bug of my own making**: my drawing code used
   `max(canvas.winfo_height(), 280)` to guard against reading the
   canvas size before it was laid out — but the *real* canvas height
   (233px) turned out to be smaller than my 280px fallback, so the code
   confidently drew content past the canvas's actual visible bounds,
   silently clipping the bottom three Fishbone labels. Fixed by reading
   the real geometry and rescheduling the draw if it isn't ready yet,
   instead of guessing a fallback number.

## How to Install

**Add:** `app/services/quality_service.py`, `app/screens/quality_screen.py`,
`tests/test_quality.py`.
**Replace:** `app/screens/main_window.py`.

## How to Run / Test

```bash
python run.py
python -m unittest discover -s tests -v   # expect 69 passed
```

Log a few bugs through the Bug Tracker screen first, then visit Quality
Monitoring to see both charts populate with your real data.
