<!-- Append to the end of AI_CONTEXT_HANDOFF.md. Do not replace the file. -->

## 17. Bug-hunt log (BUG-015 to BUG-035, Q09 Reduce Bugs)
Each bug has `docs/bugs/BUG-0NN.md` (how found, root cause, fix, test), a regression test, and an entry in `app/database/log_bugs.py` (load with `python -m app.database.log_bugs`; Mayank is reporter and fixer; bugs stay "Fixed" until closed in the Bug screen). Latest full suite: 241 tests.

| Bug | Severity | What |
|---|---|---|
| 015 | Low | Sign-up dialog could be submitted twice |
| 016 | Low | Calendar did not jump to a new event's month |
| 017, 019 | Medium | Record IDs `True` / `1.9` accepted (`validate_record_id`) |
| 018 | Medium | Open leave stayed after room release |
| 020 | Medium | CSV formula text in evidence logs |
| 021, 022 | Low | Event date window; duplicate titles ignoring case |
| 023 | High | Roles enforced only in navigation; now `session.require_roles` in services |
| 024 | High | Simultaneous allocations could overfill a room (`BEGIN IMMEDIATE`, unique indexes) |
| 025 | High | Login lockout after 5 wrong passwords (5 minutes) |
| 026 | High | Tk callback errors now logged and shown |
| 027 | High | Start-up failures shown in a window |
| 028, 029 | High | Default `admin/admin123` and seeded `Welcome123` must be changed at first login |
| 030 | High | Registration numbers case-insensitive |
| 031 | Critical | Daily verified backup + restore (`app/database/backup.py`) |
| 032 | High | Users change their own password (sidebar link) |
| 033 | High | 15-minute idle log-out |
| 034 | High | Read-only data health check (`python -m app.database.check_data`) |
| 035 | High | Defect log has reporter/fixer; old log files upgraded; write failures logged |

Conventions added: tests clear the session in `setUp`; any new service function that takes an ID uses `validate_record_id`; any staff-only service starts with `session.require_roles(...)`.

Known gaps: Devanagari names are rejected (scope decision needed); backups sit on the same disk; `hostel.db` and `app/database/backups/` hold real student data and must be gitignored; Segoe UI rendering on Windows unverified; Quality Objective IDs for CR-11 onward undefined.
