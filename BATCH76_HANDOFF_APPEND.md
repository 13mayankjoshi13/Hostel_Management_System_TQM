
## Update – roles (append; do not replace the file)

Roles: Super Admin, Administrator, Warden, Staff, Student. `session` groups: `SUPER_ROLES`, `ADMIN_ROLES` (+Super), `WARDEN_ROLES` (+Admin), `STAFF_ROLES` (+Warden/Staff), `ALL_ROLES`. Permission table: `docs/ROLES.md`. Services enforce it; `main_window.ROLE_SCREENS` decides the menu per role.
Login panels: Student, Staff (Warden+Staff), Admin, Super Admin (`auth_service.LOGIN_PANELS`).
Only Super Admin creates, resets or deletes Administrator/Super Admin accounts; last Super Admin cannot be deleted. First-run `admin` is a Super Admin; `ensure_default_admin` promotes the oldest Administrator of an older database once. No-login fallback role (`config.CURRENT_ROLE`, used by scripts and tests) is now Super Admin.
Behaviour change: wardens and staff can no longer add rooms, see bugs or quality; staff cannot add/edit students, allocate rooms or issue fines. Suite: 284 tests.
