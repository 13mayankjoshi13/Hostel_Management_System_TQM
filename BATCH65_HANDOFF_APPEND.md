
## Update – BUG-044, BUG-045 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 044 | Medium | Names must start with a letter; allotment CSV export neutralises formula text |
| 045 | High | `session.require_own_or_staff`: students act only on their own record in `record_leave`, `mark_returned`, `create_complaint` |

Total: 45 bugs. Suite: 256 tests (18 UI tests skip without a display).
Convention: any service that takes a student id must call `require_roles` (staff-only) or `require_own_or_staff`.
Commit messages carry no Co-Authored-By trailer (user request).
