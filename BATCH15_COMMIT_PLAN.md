# Commit Plan — Hosteller Feedback Features (Batch 15)

```bash
git add TQM/customer_requirements.md
git commit -m "docs: add hosteller interview and requirements CR-11 to CR-13"
git push

git add app/database/db.py app/utils/validation.py
git commit -m "feat: add leaves table, leave validation and Washroom complaint category"
git push

git add app/services/leave_service.py app/screens/leave_screen.py app/screens/main_window.py
git commit -m "feat: add leave tracking service, screen and navigation"
git push

git add app/services/allocation_service.py app/screens/allocation_screen.py
git commit -m "feat: export room allotment list to CSV"
git push

git add app/screens/complaint_screen.py
git commit -m "feat: add Washroom category to the complaint form"
git push

git add tests/test_leave.py
git commit -m "test: add module tests for leave tracking, allotment export and washroom category (Q09)"
git push

git add TQM/requirements_traceability.md docs/testing.md README.md BATCH15_README.md BATCH15_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add Batch 15 docs and update AI handoff"
git push
```
