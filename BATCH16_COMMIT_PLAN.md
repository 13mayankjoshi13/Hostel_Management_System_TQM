# Commit Plan — Student Side (Batch 16)

```bash
git add TQM/customer_requirements.md
git commit -m "docs: add student-side requirement CR-14"
git push

git add app/database/db.py app/utils/session.py app/utils/validation.py
git commit -m "feat: add Student role, session student id and users.student_id migration"
git push

git add app/services/auth_service.py
git commit -m "feat: link student accounts to student records in auth service"
git push

git add app/services/student_portal_service.py
git commit -m "feat: add student self-service service with own-data checks"
git push

git add app/screens/my_room_screen.py app/screens/my_complaints_screen.py app/screens/my_leave_screen.py
git commit -m "feat: add student portal screens"
git push

git add app/screens/main_window.py app/screens/user_screen.py
git commit -m "feat: role-based navigation and student account creation"
git push

git add tests/test_student_portal.py
git commit -m "test: add module tests for student role and portal (Q09)"
git push

git add TQM/requirements_traceability.md docs/testing.md README.md BATCH16_README.md BATCH16_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add Batch 16 docs and update AI handoff"
git push
```
