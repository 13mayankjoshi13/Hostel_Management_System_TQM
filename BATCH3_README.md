# Batch 3 — Complaint Management + UI Overhaul + Restructure

This batch does three things at once, because you asked for the visual
overhaul and the folder restructure ahead of your 15th presentation, and
Complaint Management was next in the roadmap anyway.

## 1. Complaint Management (new feature)

| File | Purpose |
|---|---|
| `app/services/complaint_service.py` | `create_complaint()`, `assign_complaint()`, `resolve_complaint()`, `get_all_complaints()` |
| `app/database/db.py` (updated) | New `complaints` table |
| `app/utils/validation.py` (updated) | `validate_complaint_category`, `validate_complaint_description`, `validate_assigned_to`, `validate_resolution_notes` |
| `app/screens/complaint_screen.py` | Log/assign/resolve UI with colored status badges |
| `tests/test_complaint.py` | 14 new tests |

**Status flow enforced by the service (Strict Validation, "invalid
complaint status → reject"):**

```
Open  --assign-->  Assigned  --resolve-->  Resolved
  \_________________resolve____________________/
```

A complaint can be resolved straight from "Open" (a warden fixing
something small without a formal assignment) or from "Assigned". It can
never move backward, and an already-Resolved complaint can never be
assigned or resolved again — every check runs before any write.

## 2. Project Restructure

`app/ui/` is gone. In its place:

```
app/
├── screens/              (was: app/ui/)
│   ├── main_window.py     — sidebar shell, wires navigation only
│   ├── student_screen.py
│   ├── room_screen.py
│   ├── allocation_screen.py
│   └── complaint_screen.py
├── services/              (unchanged location, now 4 files)
│   ├── student_service.py
│   ├── room_service.py
│   ├── allocation_service.py
│   └── complaint_service.py
├── theme.py               (new — see below)
├── database/
└── utils/
```

Each screen is now its own file instead of one large `main_window.py`
with every tab's code inside it — this matches the file-per-module
layout you asked for and is also just easier to navigate/demo from.

**You must delete your old `app/ui/` folder** when installing this batch
— see the install steps below.

## 3. Visual Overhaul

The plain white `ttk.Notebook` tabs are replaced with:

- A dark indigo **sidebar** for navigation (Students / Rooms / Room
  Allocation / Complaints) with a highlighted active item
- **Card-style panels** (`app/theme.py` → `build_card()`) instead of
  boxy `LabelFrame`s, for both forms and tables
- **Striped tables** (alternating row colors) via `style_treeview_stripes()`
- **Colored status badges** for complaints (orange = Open, blue =
  Assigned, green = Resolved)
- Consistent color palette, spacing, and fonts defined in one place:
  `app/theme.py` — change a color there and it updates everywhere

`app/theme.py` is a new shared module, not a "screen" — every screen
imports `COLORS`, `apply_theme`, and `build_card` from it.

### Proof this actually renders correctly

I don't have a display in my own environment by default, so for this
batch I installed a virtual display (Xvfb) specifically to launch the
real app, click through all four screens, add a student/room/allocation/
complaint, and assign + resolve that complaint — then screenshotted each
step. Every flow worked with no errors before this ZIP was packaged.
This is the same code you're getting; the screenshots aren't decoration
tacked on after — they caught and helped me fix a database-initialization
bug in my *test harness* (the real app was already correct via
`app/main.py`, which always calls `initialize_database()` before
launching the window).

## How to Install

1. **Delete** your existing `app/ui/` folder entirely.
2. Copy in from this ZIP: `app/theme.py` (new), the whole `app/screens/`
   folder (new), `app/database/db.py` (replace), `app/utils/validation.py`
   (replace), `app/services/complaint_service.py` (new), `app/main.py`
   (replace — one-line import change), `tests/test_complaint.py` (new).
3. Everything else (`student_service.py`, `room_service.py`,
   `allocation_service.py`, `logging_service.py`, `exception_handler.py`,
   `run.py`, `requirements.txt`) is unchanged from Batch 2 and included
   only so this ZIP is self-contained.

## How to Run

```bash
python run.py
```

## How to Test

```bash
python -m unittest discover -s tests -v
```

Expected: **45 passed** (22 validation + 9 allocation + 14 complaint).

## Known Limitations

- No window icon (Tkinter's default) — cosmetic only, doesn't affect the
  demo.
- `assigned_to` is free text, not a dropdown of staff — fine for now
  since there's no staff/user table yet.
- The sidebar is fixed-width; very small windows (below the `minsize` of
  880×560) aren't supported — shouldn't matter for a projector demo.

## Next Batch

**Bug Tracker** — the last unbuilt Q09 feature. Fields per your spec:
Bug ID, Date, Module, Category, Title, Description, Severity, Priority,
Status, Root Cause, Corrective Action, Test Case — writing real rows to
`TQM/data/defect_log.csv` as bugs are found during your own testing
(never fabricated). After that: Quality Monitoring dashboards and SQC
automation (Pareto/Fishbone/PDCA) pulling from the real CSV data this
app has been generating since Batch 1.
