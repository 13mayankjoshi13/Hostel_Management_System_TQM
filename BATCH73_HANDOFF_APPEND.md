
## Update – BUG-051 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 051 | Medium | `initialize_database` closes its connection in `finally` (a failed open left the file locked on Windows) |

CI runs the suite on windows-latest before building the exe. `test_timestamps` skips where `time.tzset` is missing. Total: 52 bug entries. Suite: 263 tests.
