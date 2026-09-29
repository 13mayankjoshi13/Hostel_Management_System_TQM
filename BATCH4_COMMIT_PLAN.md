# Commit Plan — UI Redesign (Batch 4)

```bash
git add app/theme.py
git commit -m "refactor: redesign theme — new teal/slate palette, accent-stripe cards"
git push

git add app/screens/dashboard_screen.py
git commit -m "feat: add Dashboard screen with live stats and recent activity feed"
git push

git add app/screens/main_window.py
git commit -m "refactor: replace sidebar navigation with top navbar"
git push

git add BATCH4_README.md BATCH4_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 4 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Theme | `python -c "import app.theme"` — no errors |
| Dashboard | `python run.py` — app opens directly on Dashboard, stat tiles show 0s on a fresh DB, no traceback |
| Navbar | Click each of the 5 nav pills — active pill turns teal, correct screen shows, data still loads on Students/Rooms/Allocation/Complaints |
| Full suite | `python -m unittest discover -s tests -v` — all 45 still pass (no logic changed, this just confirms nothing broke) |
| Evidence link | Add a student via the UI, go to Dashboard, confirm it appears in "Recent Activity" |

## Running Total

This batch contributes **4 commits**, bringing the project total to
**24 commits**.

## Next Batch

Back to the roadmap: **Bug Tracker** (Q09 feature #4) — the last
unbuilt piece, writing real rows to `TQM/data/defect_log.csv`.
