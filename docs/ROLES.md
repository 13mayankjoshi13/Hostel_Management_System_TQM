# Roles and what each can do

| Feature | Super Admin | Admin | Warden | Staff | Student |
|---|---|---|---|---|---|
| Dashboard | yes | yes | yes | yes | own home |
| Students (add, edit, delete) | yes | yes | yes | view only | own details |
| Rooms (add, delete) | yes | yes | – | – | own room |
| Room allocation / release | yes | yes | yes | view only | – |
| Complaints (assign, resolve) | yes | yes | yes | yes | own |
| Leaves | yes | yes | yes | – | own |
| Fines (issue, cash, waive) | yes | yes | yes | – | own, pay online |
| Workers (add, deactivate) | yes | yes | – | – | – |
| Workers (attendance, job list) | yes | yes | – | yes | – |
| Calendar events (edit) | yes | yes | yes | read | read |
| Bug tracker, Quality | yes | yes | – | – | – |
| User accounts: Warden, Staff, Student | yes | yes | – | – | – |
| User accounts: Admin, Super Admin | yes | – | – | – | – |

Each role signs in on its own tab of the login screen (Student, Staff, Admin, Super Admin; Warden and Staff share the Staff tab) and sees only its own menu. The services enforce the same table, so a hidden screen cannot be reached by other means.
Default first-run account: `admin` is a **Super Admin** and must change its password at first login. An existing database promotes its oldest Administrator to Super Admin once.

## Batch 77 additions

| Feature | Super Admin / Admin | Warden | Staff | Student |
|---|---|---|---|---|
| Send notices (all, a hostel, one student) | yes | yes | yes | – |
| Delete notices | yes | – | – | – |
| Roll call (Present / Absent) | yes | yes | yes | own summary |
| Wardens (add, remove) | yes | – | – | sees own gender's warden |
| Emergency numbers (add, remove) | yes | – | – | read |

Students have a gender; rooms have a floor and an optional Boys/Girls hostel. A Boys room only takes male students and a Girls room only female students. Only the national numbers (112, 100, 101, 108, 1091) are pre-filled; add your university's own numbers in Wardens & Emergency.

## Batch 78 additions

- Student front page ("Home"): own attendance (30 days), fines due, latest notices for them, their gender's warden, upcoming events and emergency numbers. A student only ever sees their own data.
- Hostel Map: every role sees rooms by hostel and floor with bed counts; names of occupants are shown to staff roles only, students see counts and a star on their own room.
- Hostel Events: everyone reads upcoming events (filter by type); Wardens and admins add or delete them.
- Staff, Warden and admin dashboards add Present / Absent today and a Notices tab.

## Batch 79 additions

- **Settings** is in every role's footer link. Appearance (light/dark theme, accent colour) is saved per user; the last choice is used on the login screen of that computer. Colours too light for white button text are rejected.
- Audit log viewer, student data download and **Quality Monitoring** are inside Settings for Administrator and Super Admin only. Quality Monitoring is no longer in the main menu.
- Every student data download is written to the audit log.

## Batch 80 additions

Quality Monitoring (Settings, Administrator and Super Admin only) now has seven tabs: Defects (Pareto, fishbone), Six Sigma (DPMO, sigma level, p-chart), Variance, Taguchi (S/N and loss), FMEA (editable, RPN), SIPOC (editable) and Poka-Yoke (controls with the test that proves each).
Definitions are stated on each tab. Six Sigma and Variance count audit-log rows as operations and error-log rows as defects, and show "not enough data" below 5 days. Taguchi uses complaint resolution time; its tolerance (D0) and cost (A0) are your own settings. Nothing is estimated or pre-filled except the SIPOC rows, which describe how the application works.
