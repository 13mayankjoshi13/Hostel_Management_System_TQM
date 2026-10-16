# Customer Requirements

## Project

**Hostel Management System**

## Primary Customer

**Hostel Administration / Hostel Warden**

This is the proposed primary operational customer for this implementation because the hostel administration is responsible for hostel operations, including room allocation and complaint handling.

## Users and Stakeholders

- Hostel Warden
- Hostel Administrator
- Hostel Staff
- System Administrator
- Students / Hostellers

## Customer Needs

1. Accurate student information.
2. Reliable room information.
3. Correct room allocation.
4. Clear room availability.
5. Complaint tracking.
6. Traceability of important operations.
7. Fewer software failures.
8. Useful error information for investigation.
9. Easy-to-use workflows.
10. Measurable quality information.

## Measurable Requirements

| ID | Customer Requirement | Measurement | Target |
|---|---|---|---|
| CR-01 | Student records should be accurate. | Invalid records accepted | 0 |
| CR-02 | Duplicate student records should be prevented. | Duplicate records accepted | 0 |
| CR-03 | Room availability should be correct. | Incorrect status in defined tests | 0 |
| CR-04 | Duplicate room allocation should be prevented. | Duplicate allocations accepted | 0 |
| CR-05 | Complaints should be traceable. | Complaints without status | 0 |
| CR-06 | Software errors should be recorded. | Detected system errors without required logs | 0 |
| CR-07 | Confirmed defects should be trackable. | Confirmed defects without tracker entry | 0 |
| CR-08 | Critical modules should have tests. | Critical modules without defined tests | 0 |
| CR-09 | Important operations should be auditable. | Defined operations without audit record | 0 |
| CR-10 | User-facing errors should be understandable. | Defined error tests with unusable feedback | 0 |

## Requirement Trace

Customer Requirement → Quality Objective → Software Feature → Test → Evidence

Example:

CR-06 → QO-04 → Error Logs → Error Logging Test → `TQM/data/error_logs.csv`

## Voice of the Customer — Hosteller Interview (28/09/2026)

An informal conversation with a resident hosteller listed the following needs:

- complaint filing for food;
- room maintenance and washroom complaints;
- a room allotment list;
- tracking which student has gone on leave and from which room.

Resulting requirements (added Batch 15):

| ID | Customer Requirement | Measurement | Target |
|---|---|---|---|
| CR-11 | Complaints should cover the issues hostellers actually report (food, maintenance, washroom). | Reported complaint types without a category | 0 |
| CR-12 | A room allotment list should be available. | Allotment list unavailable for export | 0 |
| CR-13 | Student leave should be traceable to a room. | Leaves recorded without an active room allocation | 0 |

## Student-side Access (Batch 16)

Hostellers are stakeholders (see Users and Stakeholders), so they get their own login and see only their own records.

| ID | Customer Requirement | Measurement | Target |
|---|---|---|---|
| CR-14 | A hosteller can see their own room, file complaints, follow their status and record leave, and cannot see or change another student's records. | Cross-student data accesses allowed in defined tests | 0 |

## Calendar and Visual Design (Batch 18)

| ID | Customer Requirement | Measurement | Target |
|---|---|---|---|
| CR-15 | Everyone can see holidays and hostel events in a calendar; only an Administrator or Warden can change them. | Calendar changes allowed for other roles in defined tests | 0 |

Default holiday dates come from the 2026 Central Government list and may differ from the university calendar; edit them in the Calendar screen.

## Student Sign-up, Self-service and Bug Visibility (Batch 29)

| ID | Customer Requirement | Measurement | Target |
|---|---|---|---|
| CR-16 | A student can request an account from the login screen, but cannot log in until an Administrator approves it. | Pending accounts that could log in in defined tests | 0 |
| CR-17 | Student details can be edited by the hostel office, and by each student for their own name and contact; the student list can be sorted. | Edits allowed to another student's record in defined tests | 0 |
| CR-18 | The Bug Tracker shows open and solved bugs, who reported each bug and who fixed it. | Bugs without a reporter, or fixed bugs without a fixer, in defined tests | 0 |
