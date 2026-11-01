
## Update – notices, attendance, wardens (append; do not replace the file)

New tables: `wardens`, `emergency_contacts`, `notices`, `student_attendance`; guarded ALTERs add `students.gender`, `rooms.floor`, `rooms.hostel_type`.
Services: `notice_service` (staff send to All/Boys/Girls/one student; students read their own), `attendance_service` (staff mark Present/Absent; approved leave reads as Leave; `student_summary`, `attendance_counts` for dashboards), `warden_service` (`warden_for_student` matches the student's gender), `emergency_service` (national numbers seeded on start; university numbers added by admins).
Rule: a Boys room takes only Male students, a Girls room only Female; gender cannot change while it conflicts with the current room. Rooms without a hostel type stay unrestricted (old data).
Screens: Notices, MyNotices, Attendance, Contacts (Wardens & Emergency, in every role's menu). Suite: 294 tests.
Next: Batch 78 role-specific dashboards, hostel map and floor details, events.
