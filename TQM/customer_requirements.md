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
