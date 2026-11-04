# Test accounts

Created/refreshed on every app start by `seed_test_accounts_and_data` (no forced password change).

| Panel | Username | Password | Notes |
|---|---|---|---|
| Super Admin | superadmin | admin123 | full access, marks attendance |
| Super Admin | admin | admin123 | |
| Admin | hostel_admin | admin123 | marks attendance |
| Warden | warden | warden123 | no attendance marking |
| Staff | hostel_staff | staff123 | no attendance marking |
| Mess Staff | mess_staff | mess123 | food complaints, daily menu, meal feedback |
| Maintenance Staff | maintenance_staff | maint123 | maintenance and washroom complaints |
| Security Staff | security_staff | security123 | visitor log and gate log only |
| Housekeeping Staff | housekeeping_staff | house123 | cleanliness complaints, cleaning checklist |
| Student (boy) | student / mayankjoshi13 | student123 | Mayank Joshi |
| Student (girl) | student_girl | student123 | Neha Rawat, girls block |

Preloaded: 14 days of attendance, notices for every audience, leaves, complaints, events, fines, wardens, workers.

Warning: the seeder resets these passwords at every start. Remove the call in `app/main.py` before real use.
