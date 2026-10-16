# Commit Plan — Sign-up, Edit/Sort, Bug Visibility (Batch 29)

```bash
git add app/database/db.py app/services/auth_service.py app/screens/signup_screen.py app/screens/login_screen.py app/screens/user_screen.py
git commit -m "feat: add student sign-up with administrator approval" 
git push

git add app/services/student_service.py app/services/student_portal_service.py app/screens/student_screen.py app/screens/my_details_screen.py app/screens/main_window.py
git commit -m "feat: edit and sort students, add My Details for students"
git push

git add app/services/bug_service.py app/services/quality_service.py app/screens/bug_screen.py app/screens/quality_screen.py app/database/log_bugs.py app/theme.py
git commit -m "feat: show open and solved bugs with reporter and fixer, scrollable quality screen" 
git push

git add tests/test_requests_batch.py
git commit -m "test: add module tests for sign-up, student edit/sort and bug people" 
git push

git add README.md docs/testing.md TQM/customer_requirements.md TQM/requirements_traceability.md BATCH29_README.md BATCH29_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add Batch 29 docs and update AI handoff" 
git push

```
