# Commit Plan — Complaint Management + UI Overhaul (Batch 3)

Split so the restructure, the visual work, and the new feature are each
reviewable on their own.

```bash
git rm -r app/ui
git commit -m "refactor: remove app/ui in favor of app/screens (see next commits)"
git push

git add app/theme.py
git commit -m "feat: add central theme module for consistent styling"
git push

git add app/screens/main_window.py app/screens/student_screen.py app/screens/room_screen.py app/screens/allocation_screen.py app/main.py
git commit -m "refactor: split UI into per-screen files with sidebar navigation"
git push

git add app/database/db.py
git commit -m "feat: add complaints table"
git push

git add app/utils/validation.py
git commit -m "feat: add complaint validation rules (Q09)"
git push

git add app/services/complaint_service.py
git commit -m "feat: add complaint management service with status-transition pipeline"
git push

git add app/screens/complaint_screen.py
git commit -m "feat: add Complaint Management screen with status badges"
git push

git add tests/test_complaint.py
git commit -m "test: add module tests for complaint management (Q09)"
git push

git add BATCH3_README.md BATCH3_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 3 README, commit plan, and AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Remove `app/ui` | `python run.py` should now fail with `ModuleNotFoundError` until the next commit lands — expected, don't push this alone to a shared branch if others rely on `main` running |
| Theme module | `python -c "import app.theme"` — no errors |
| Screens split | `python run.py` — sidebar shows, all 4 nav items switch screens |
| Complaints table | `python -c "from app.database.db import initialize_database; initialize_database(); print('OK')"` |
| Validation | `python -m unittest tests.test_validation -v` |
| Complaint service | `python -m unittest tests.test_complaint -v` |
| Complaint screen | `python run.py` — log a complaint, assign it, resolve it, confirm the status badge color changes each time |
| Full suite | `python -m unittest discover -s tests -v` — all 45 pass |

## Running Total

This batch contributes **9 commits**, bringing the project total to
**20 commits** across the documentation foundation, Batch 1, Batch 2,
and Batch 3 — over halfway to the 30+ the course expects, with Bug
Tracker, Quality Monitoring, and SQC automation still to come.

## Next Batch

**Bug Tracker** (`app/services/bug_service.py`), writing to
`TQM/data/defect_log.csv` with the exact fields from your spec (Bug ID,
Date, Module, Category, Title, Description, Severity, Priority, Status,
Root Cause, Corrective Action, Test Case).
