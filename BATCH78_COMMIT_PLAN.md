# Batch 78 – Role dashboards, hostel map, events

```
git add app/services/home_service.py
git commit -m "feat: home data for students (attendance, fines, notices, warden, events) and the hostel floor plan"

git add app/screens/student_home_screen.py app/screens/hostel_map_screen.py app/screens/events_screen.py app/screens/main_window.py
git commit -m "feat: student home page, hostel map with floor details, hostel events screen"

git add app/screens/dashboard_screen.py
git commit -m "feat: attendance today and notices on the staff dashboard"

git add tests/test_home.py tests/test_batch77_screens_ui.py tests/test_roles.py
git commit -m "test: cover home data, floor plan privacy and the new screens"

git add docs/ROLES.md BATCH78_COMMIT_PLAN.md BATCH78_HANDOFF_APPEND.md
git commit -m "docs: Batch 78 handoff"

git push
```

Apply after Batch 77. After pulling, append `BATCH78_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
