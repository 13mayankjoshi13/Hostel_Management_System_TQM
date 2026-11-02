
## Batch 83
- Attendance: mark_attendance and get_roster are ADMIN_ROLES only; attendance_counts stays STAFF_ROLES (read-only totals). Attendance removed from Warden/Staff menus.
- Dashboard: quick actions and KPI cards built per role on every refresh; Dashboard/StudentHome auto-refresh every 30 s.
- Scrolling: theme.split_layout left column is a ScrollFrame.
- Seed: genders, hostel types, floors; student_girl account; 14 days attendance (no longer overwrites marked rows); seeded event kinds fixed; calendar tolerates unknown kinds.
- docs/TEST_ACCOUNTS.md lists credentials. Startup seeder resets those passwords each run.
- Tests: 333 pass.
