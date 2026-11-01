# Batch 77 – Notices, attendance, wardens and emergency numbers

```
git add app/database/db.py app/utils/validation.py
git commit -m "feat: tables for wardens, notices, emergency numbers and attendance; student gender, room floor and hostel type"

git add app/services/student_service.py app/services/room_service.py app/services/allocation_service.py
git commit -m "feat: gender on students, floor and Boys/Girls hostel on rooms, gender rule in room allocation"

git add app/services/notice_service.py app/services/attendance_service.py app/services/warden_service.py app/services/emergency_service.py app/main.py
git commit -m "feat: notices, roll call attendance, gender-matched wardens and emergency numbers"

git add app/screens/notice_screen.py app/screens/my_notices_screen.py app/screens/attendance_screen.py app/screens/contacts_screen.py app/screens/student_screen.py app/screens/room_screen.py app/screens/main_window.py
git commit -m "feat: Notices, My Notices, Attendance and Wardens & Emergency screens; gender and floor fields"

git add tests/test_notices_attendance.py tests/test_batch77_screens_ui.py tests/test_roles.py
git commit -m "test: cover notices, attendance, wardens, emergency numbers and the new screens"

git add docs/ROLES.md BATCH77_COMMIT_PLAN.md BATCH77_HANDOFF_APPEND.md
git commit -m "docs: Batch 77 permissions and handoff"

git push
```

Apply after Batch 76. After pulling, append `BATCH77_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
