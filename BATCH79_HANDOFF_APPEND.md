
## Update – Settings and themes (append; do not replace the file)

`theme.set_appearance(mode, accent)` rewrites `COLORS` (light/dark base + accent-derived soft/hero colours); widgets read `COLORS` when built, so `MainWindow._change_appearance()` destroys and rebuilds the whole UI. Appearance is stored in new table `app_settings` (`appearance:<user>` and `appearance:last`) by `settings_service`; accent must be #RRGGBB with luminance <= 0.45.
`SettingsScreen` (footer link, all roles): Appearance; admin-only tabs Audit log (`audit_service.read_audit_log`), Data download (`export_students_csv`, audited, UTF-8 BOM) and Quality Monitoring (the existing QualityScreen, no longer in the main menu). Settings is built after login (`_enter_user_ui`) because the tabs depend on the role.
Sidebar is now scrollable (admins have many entries). Dashboard KPIs split into two rows. Suite: 307 tests. Dark mode checked by screenshots under Xvfb only; Quality charts still use fixed colours that are dim in dark mode (fixed in Batch 80).
