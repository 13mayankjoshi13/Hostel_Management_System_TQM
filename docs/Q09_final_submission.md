# Q09 – Reduce Bugs: Final Submission

**Project:** Hostel Management System (Python, SQLite, Tkinter)
**Student:** Mayank Joshi · CSE · Roll 2410302037
**Subject:** BBAT104 – Total Quality Management
**Assigned goal:** Q09 Reduce Bugs

## 1. Goal and approach
Reduce defects by preventing them (validation and service-level rules), containing them (exception handling), detecting them (tests) and recording them (bug tracker and logs). Each bug was handled the same way: find, fix at the root cause, add a regression test that fails without the fix, log it in the database, and document it in `docs/bugs/BUG-NNN.md`.

## 2. The five required features
| Feature | What was built | Evidence |
|---|---|---|
| Exception handling | Services convert database and file errors into `ValidationError`; screens show a message and log the error; unhandled Tk callback errors are caught and shown; start-up failures are shown in a window | `app/main.py`, `app/utils/logging_service.py`, `tests/test_bug_fixes.py` (BUG-026, 027) |
| Strict validation | One validator per field, run before any write: names, registration numbers, contact numbers, room data, dates, passwords, usernames, complaint and bug fields | `app/utils/validation.py` |
| Module tests | One test module per area plus regression tests per bug | `tests/` (262 tests; 18 UI tests skip when no display is available) |
| Bug tracker | Database table with status workflow Open → In Progress → Fixed → Closed, root cause, corrective action and test case per bug; Pareto and fishbone views | `app/services/bug_service.py`, `app/services/quality_service.py`, `app/database/log_bugs.py` |
| Error logs | Append-only CSV logs for errors, audit trail and defects; formula-safe; queued in a `.pending` file when a file is locked; repaired if re-saved by Excel | `TQM/data/*.csv`, `app/utils/logging_service.py` |

## 3. Bugs found and fixed
`app/database/log_bugs.py` holds **51 logged defects**, all with status Fixed and a regression test.

| By severity | Count |
|---|---|
| Critical | 2 |
| High | 24 |
| Medium | 13 |
| Low | 12 |

| By category | Count |
|---|---|
| Security | 15 |
| Data Integrity | 14 |
| Validation | 11 |
| Functional | 6 |
| UI/UX | 5 |

| By module | Count |
|---|---|
| Other (logging, accounts, backup tooling) | 21 |
| Allocation | 7 |
| UI | 7 |
| Student | 6 |
| Database | 6 |
| Room | 3 |
| Complaint | 1 |

Pareto reading: Security and Data Integrity together account for 29 of 51 (57%). Adding Validation brings it to 40 of 51 (78%), and Functional to 46 of 51 (90%).

### Most important fixes
- **Data protection:** room overfill under simultaneous allocation (BUG-024); daily verified backup and restore (BUG-031, 043, 047, 050); read-only data check at start-up (BUG-034).
- **Access control:** staff-only rules enforced in the services, not only in the menu (BUG-023); students cannot read or act on other students' records (BUG-036, 045).
- **Accounts:** login lockout (BUG-025), forced change of default passwords (BUG-028, 029), password reset unlocks and expires (BUG-046), no username disclosure at login (BUG-037), sign-up guessing lockout (BUG-038), idle log-out (BUG-033).
- **Evidence integrity:** formula-safe logs and exports (BUG-020, 044), logs survive Excel locking and re-saving (BUG-041, 042), correct local times (BUG-039).
- **Input handling:** case-insensitive registration numbers (BUG-030), Hindi names (BUG-048), phone numbers as people write them (BUG-049).

## 4. How the work was done
Defects were found by reading the code, probing the validators and services with realistic and hostile input, automated random input testing, and driving the screens on a virtual display. Code review and probing were carried out with AI assistance (Claude, Anthropic); the developer reviewed, applied and committed every change. Every bug has a regression test confirmed to fail when its fix is removed.

## 5. Test results
- Full suite: **262 tests, all passing** (18 UI tests are skipped on machines without a display).
- Run with: `python -m unittest discover -s tests -t .`

## 6. Not yet measured / limitations
- **Quality measures** (defect density per module, escaped-defect rate, time to fix): **not yet measured**. They need data collected over real use and are not claimed here.
- Defects were found by the developer and the assistant, not by independent testers or real hostel users; no user acceptance testing has been done.
- The screens were checked on a Linux virtual display only; appearance on Windows is not yet verified.
- Existing duplicate records are reported by the data check but not merged automatically.
- The dashboard room grid is untested above about 1,500 rooms.
- The off-disk backup copy works only where `HOSTEL_EXTRA_BACKUP_DIR` is set.
