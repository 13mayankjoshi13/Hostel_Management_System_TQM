
## Batch 84
- Visitors: visitors table, visitor_service, VisitorScreen (all staff roles); flags After hours (9-19) and Overstayed.
- Leave approval: leaves.status Pending/Rejected, decided_by/decided_at/decision_note columns; student applications start Pending, decide_leave (WARDEN_ROLES) notifies the student; releasing an allocation rejects pending leaves.
- Attendance: monthly_report and export_report_csv (ADMIN_ROLES), 75% low threshold; Monthly report tab on Attendance screen. student_summary now counts only On Leave/Returned leaves.
- Badges: notice_reads table, unread_count/mark_all_read; sidebar badge for My Notices (students) and Leaves (pending, Warden+); refreshed every 30 s.
- Global search: search_service + top-bar box (staff roles).
- Seed: pending leave and 4 sample visitors.
- Tests: 341 pass.
