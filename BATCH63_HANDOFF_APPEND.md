
## Update – BUG-036 to BUG-043 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 036 | High | Student sessions could read all students' complaints, allocations and the allotment export |
| 037 | Medium | Login no longer reveals which usernames exist |
| 038 | High | Sign-up lockout (`signup_attempts`) stops guessing a classmate's contact number |
| 039 | High | Times shown in local time (`app/utils/timefmt.py`), stored in UTC; legacy local-ISO rows converted |
| 040 | High | Log-in window can be closed and the app quit from it |
| 041 | High | Log rows queued in `<log>.csv.pending` while a CSV is locked (Excel) |
| 042 | High | Windows-encoded logs repaired to UTF-8; error ids = highest + 1 |
| 043 | High | Restore requires the hostel tables; failed backups leave no partial file |

Total: 43 bugs found, fixed, regression-tested, logged and written up. Suite: 254 tests (18 UI tests skip without a display).

New conventions: `.pending` files and `hostel.db` must be gitignored; log writers never raise; displayed times go through `timefmt`.

Known gaps unchanged: Devanagari names rejected; backups on the same disk; Windows rendering unverified; no quality results measured yet.
