# Batch 4 — Complete UI Redesign (No New Backend Features)

You said other students had copied the Batch 3 look, so this batch is a
**ground-up visual change**, not a recolor. No service, validation, or
database logic changed at all — same 45 tests, same behavior, only the
presentation layer is different. Safe to install even close to your
demo date.

## What Changed vs. Batch 3

| Aspect | Batch 3 | Batch 4 |
|---|---|---|
| Navigation | Dark **left sidebar** | Dark **top navbar** with pill buttons |
| Palette | Indigo | Teal / slate |
| Cards | Full grey border box | White card, thin border, **colored top accent stripe** |
| Landing screen | Students tab | **New Dashboard** — live stat tiles + recent activity feed |
| Table headers | Indigo-tinted | Teal-tinted, smaller/tighter |

## New: Dashboard Screen

`app/screens/dashboard_screen.py` — opens by default now. Shows:

- **4 live stat tiles**: Total Students, Rooms Occupied (%), Active
  Allocations, Open Complaints — computed from the real service layer,
  never hard-coded.
- **Recent Activity panel** reading the tail of
  `TQM/data/audit_logs.csv` directly — this is a genuinely useful thing
  to show your evaluator: the software isn't just writing to a CSV
  nobody looks at, it's feeding it back into the UI as live evidence.
  Handles the empty-file case gracefully on a fresh install.

## Files Changed

| File | What |
|---|---|
| `app/theme.py` | Completely rewritten — new color tokens, `build_stat_card()` added, `build_card()` now draws an accent stripe instead of a plain border |
| `app/screens/main_window.py` | Completely rewritten — top navbar instead of sidebar, 5 nav items (Dashboard added) |
| `app/screens/dashboard_screen.py` | **New file** |
| `app/screens/student_screen.py`, `room_screen.py`, `allocation_screen.py`, `complaint_screen.py` | **Unchanged** — they already read all their styling from `app/theme.py`, so the new look applies automatically with zero edits to these files |

## Proof It Renders Correctly

Same as Batch 3: I launched the actual app under a virtual display,
clicked through all 5 screens, added a student/room/allocation/complaint,
assigned the complaint, and screenshotted each step before packaging.
No errors, no layout breakage. The Dashboard screenshots show both the
empty state (fresh install) and the filled state (after adding data).

## How to Install

1. Copy `app/theme.py` into your project — **replace** the existing one.
2. Copy `app/screens/main_window.py` — **replace** the existing one.
3. Copy `app/screens/dashboard_screen.py` — **new file**, add it.
4. Nothing else needs to change. `student_screen.py`, `room_screen.py`,
   `allocation_screen.py`, `complaint_screen.py`, all services, all
   tests — untouched, included here only so the ZIP is self-contained.

## How to Run

```bash
python run.py
```

You'll land on the Dashboard first now instead of the Students tab.

## How to Test

```bash
python -m unittest discover -s tests -v
```

Expected: **45 passed** — unchanged from Batch 3, since no logic changed.

## If You Want It to Look Even More Different

Everything is controlled from `app/theme.py`'s `COLORS` dict at the top
of the file — swap `"primary": "#0D9488"` for any other hex color and
every button, active nav pill, and card accent updates everywhere at
once. Good options if teal still feels close to something else you've
seen: `#7C3AED` (violet), `#DB2777` (pink), `#EA580C` (orange).
