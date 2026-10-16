# Batch 29 — Sign-up, Edit/Sort, Bug Visibility

1. Student sign-up on the login screen; accounts stay Pending until an Administrator approves them.
2. Edit student details (Students screen for staff, My Details for students); sort the student list.
3. Bug Tracker: Open / Solved filter, Reported and Fixed by columns (Mayank for BUG-001 to BUG-009), detail of how each bug was fixed.
4. Quality Monitoring scrolls on small windows and lists who found and who fixed bugs.

Copy over the project, run `python -m app.database.log_bugs` once, then `python -m unittest discover -s tests -t .` (195 tests passing).
Existing databases are upgraded automatically (new columns). Not verified: Segoe UI look on Windows.
