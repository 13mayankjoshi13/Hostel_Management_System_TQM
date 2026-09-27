# Commit Plan — Application Foundation (Batch 1)

Split into small, meaningful commits rather than one large commit, so
the Git history demonstrates incremental TQM-driven development.

```bash
git add app/config.py app/database/db.py requirements.txt run.py
git commit -m "feat: add SQLite database layer and app configuration"
git push

git add app/utils/validation.py
git commit -m "feat: add strict validation foundation (Q09)"
git push

git add app/utils/logging_service.py app/utils/exception_handler.py
git commit -m "feat: add central exception handler and error/audit logging (Q09)"
git push

git add app/services/student_service.py app/services/room_service.py
git commit -m "feat: add student and room services with duplicate prevention"
git push

git add app/ui/main_window.py app/main.py
git commit -m "feat: add Tkinter GUI foundation for students and rooms"
git push

git add tests/test_validation.py
git commit -m "test: add module tests for validation and service duplicate rules (Q09)"
git push

git add APP_README.md APP_COMMIT_PLAN.md
git commit -m "docs: add application foundation README and commit plan"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Database + config | `python -c "from app.database.db import initialize_database; initialize_database(); print('OK')"` |
| Validation | `python -m unittest tests.test_validation.TestStudentNameValidation -v` (and the other validation classes) |
| Logging / exception handler | Delete `app/database/hostel.db`, run `python run.py`, add a student, confirm `TQM/data/audit_logs.csv` gained a row |
| Services | `python -m unittest tests.test_validation.TestServiceLayerWithTempDatabase -v` |
| GUI | `python run.py` — add one student and one room, confirm both list correctly |
| Full test suite | `python -m unittest discover -s tests -v` — all tests pass |

## Running Total

This batch contributes **7 commits**. Combined with the documentation
foundation batch's commits, this keeps the project on track for the
30+ meaningful commits the course expects.
