
## Batch 87: specialist staff roles
- New roles: Mess Staff, Maintenance Staff, Security Staff, Housekeeping Staff (Staff login tab). Not part of STAFF_ROLES; session.py has explicit groups (SPECIALIST_ROLES, ROLE_CATEGORIES, VISITOR_ROLES, GATE_ROLES, MESS_*_ROLES, CLEANING_*_ROLES).
- New services: mess_service, gate_service, housekeeping_service, duty_service; new tables meal_menu, meal_feedback, gate_log, cleaning_checks.
- New screens: Duty (home), Mess, MyMess (students), Gate, Cleaning. complaint_service: take_complaint, get_my_queue, category check.
- Test accounts: mess_staff/mess123, maintenance_staff/maint123, security_staff/security123, housekeeping_staff/house123.
- Tests: 351 pass (tests/test_batch87.py added; test_roles distinct-role count 4 to 8).
- Open: seeder still resets test passwords at startup; quality metrics for this batch not measured.
