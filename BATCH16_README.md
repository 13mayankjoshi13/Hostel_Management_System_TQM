# Batch 16 — Student Side

- New `Student` role; accounts are created by an Administrator in User Management and linked to a student record.
- Students see only: My Room, My Complaints (file + follow status), My Leave (apply + mark returned).
- All portal functions use the logged-in student from the session, so one student cannot see or change another's data.
- Staff roles never see the student screens; students never see staff screens.
- Existing databases get `users.student_id` automatically.

Docs updated: `TQM/customer_requirements.md` (CR-14), `TQM/requirements_traceability.md`, `docs/testing.md`, `README.md`, `AI_CONTEXT_HANDOFF.md`. Replace earlier copies.

Tests: 132 pass. Not verified: new screens visually (no tkinter in build environment). Limits: see handoff section 13.
