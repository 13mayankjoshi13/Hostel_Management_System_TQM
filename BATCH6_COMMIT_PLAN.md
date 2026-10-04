# Commit Plan — Professional UI Redesign (Batch 6)

```bash
git add app/theme.py
git commit -m "refactor: redesign theme — neutral palette, one accent, flat panels, new helpers"
git push

git add app/screens/splash_screen.py
git commit -m "refactor: restyle splash screen — minimal, no icon, shorter duration"
git push

git add app/screens/main_window.py
git commit -m "refactor: replace hub-and-spoke navigation with a persistent plain-text sidebar"
git push

git add app/screens/dashboard_screen.py
git commit -m "refactor: simplify Dashboard to a KPI strip + activity table (sidebar now handles nav)"
git push

git add app/screens/student_screen.py app/screens/room_screen.py app/screens/allocation_screen.py app/screens/complaint_screen.py
git commit -m "refactor: unbox forms, use bordered table panels, remove redundant breadcrumbs"
git push

git add BATCH6_README.md BATCH6_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 6 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Theme | `python -c "import app.theme"` — no errors |
| Splash | `python run.py` — brief, no clipped text |
| Sidebar | Click each of the 5 items — correct screen shows, active item gets the left accent bar |
| Dashboard | Confirm KPI strip shows correct live counts, activity table lists real audit rows |
| Forms | Add a student/room/allocation/complaint — confirm validation errors still show correctly |
| Full suite | `python -m unittest discover -s tests -v` — all 45 still pass |

## Running Total

This batch contributes **6 commits**, bringing the project total to
**~36 commits** — comfortably past the 30+ the course expects.

## Next Batch

Back to the roadmap: **Bug Tracker** (Q09 feature #4) — writing real
rows to `TQM/data/defect_log.csv`.
