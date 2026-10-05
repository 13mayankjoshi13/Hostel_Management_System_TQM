# Commit Plan — Bug Tracker (Batch 7)

```bash
git add app/database/db.py
git commit -m "feat: add bugs table"
git push

git add app/utils/validation.py
git commit -m "feat: add bug tracker validation rules (Q09)"
git push

git add app/utils/logging_service.py
git commit -m "feat: add log_defect() writing to TQM/data/defect_log.csv"
git push

git add app/services/bug_service.py
git commit -m "feat: add bug tracker service with forward-only status pipeline (Q09)"
git push

git add app/screens/bug_screen.py app/screens/main_window.py
git commit -m "feat: add Bug Tracker screen and sidebar entry"
git push

git add app/screens/dashboard_screen.py
git commit -m "feat: add Open Bugs stat to Dashboard"
git push

git add tests/test_bug.py
git commit -m "test: add module tests for bug tracker pipeline (Q09)"
git push

git add BATCH7_README.md BATCH7_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 7 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Database | `python -c "from app.database.db import initialize_database; initialize_database(); print('OK')"` |
| Validation | `python -m unittest tests.test_validation -v` |
| Logging | `python -m unittest tests.test_bug -v` |
| Bug service | same |
| Screen | `python run.py` — log a bug, Start Progress, Mark Fixed (fill all 3 prompts), Close Bug; confirm status color changes each step |
| Dashboard stat | After closing all bugs, confirm "Open Bugs" reads 0; log a new one, confirm it reads 1 |
| Full suite | `python -m unittest discover -s tests -v` — all 62 pass |
| Evidence | Open `TQM/data/defect_log.csv` after using the app — confirm multiple rows per bug (one per status change) |

## Running Total

This batch contributes **8 commits**, bringing the project total to
**~44 commits**.

## Next

All five Q09 features are built. Suggested next steps: Quality
Monitoring dashboard, SQC automation (Pareto/Fishbone from
`defect_log.csv`), or a final documentation pass once real usage data
exists.
