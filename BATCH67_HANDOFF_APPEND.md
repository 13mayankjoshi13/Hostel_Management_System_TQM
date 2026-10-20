
## Update – BUG-047 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 047 | High | Optional `HOSTEL_EXTRA_BACKUP_DIR`: daily backup also copied off the database disk (7-day retention); failure logged as `BackupCopyError` |

Total: 47 bugs. Suite: 258 tests (18 UI tests skip without a display).
Known gap closed: "backups sit on the same disk" (only if the variable is set on the machine).
