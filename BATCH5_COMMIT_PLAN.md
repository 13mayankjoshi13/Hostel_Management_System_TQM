# Commit Plan — Full Layout + Color Redesign (Batch 5)

```bash
git add app/theme.py
git commit -m "refactor: redesign theme for dark mode — navy/cyan palette, module-tile and breadcrumb helpers"
git push

git add app/screens/splash_screen.py
git commit -m "feat: add splash screen on launch"
git push

git add app/screens/dashboard_screen.py
git commit -m "feat: turn Dashboard into a navigation hub with clickable module tiles"
git push

git add app/screens/main_window.py
git commit -m "refactor: replace top navbar with slim topbar + hub-and-spoke navigation"
git push

git add app/screens/student_screen.py app/screens/room_screen.py app/screens/allocation_screen.py app/screens/complaint_screen.py
git commit -m "feat: add breadcrumb navigation to all module screens; fix unthemed complaint description box"
git push

git add BATCH5_README.md BATCH5_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 5 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Theme | `python -c "import app.theme"` — no errors |
| Splash | `python run.py` — splash shows ~1.6s with no clipped text, then Dashboard appears |
| Dashboard hub | Click each of the 4 module tiles — correct screen opens each time |
| Breadcrumb | From any module screen, click "🏠 Dashboard" — returns to the hub |
| Complaint form | Log a complaint — confirm the description box is dark-themed, not a white box |
| Full suite | `python -m unittest discover -s tests -v` — all 45 still pass |
| Evidence link | Add a student, go to Dashboard, confirm it's in "Recent Activity" |

## Running Total

This batch contributes **6 commits**, bringing the project total to
**30 commits** — you've hit the 30+ the course expects, with Bug
Tracker, Quality Monitoring, and SQC automation still ahead for extra
depth.

## Next Batch

Back to the roadmap: **Bug Tracker** (Q09 feature #4) — writing real
rows to `TQM/data/defect_log.csv`.
