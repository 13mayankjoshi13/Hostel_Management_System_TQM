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
