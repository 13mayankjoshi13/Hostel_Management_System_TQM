# Requirements Traceability Matrix

| Customer Req. | Quality Objective | Software Feature | TQM Concept | Test Evidence |
|---|---|---|---|---|
| CR-01 | QO-01 | Student validation | Error Prevention | Student validation tests |
| CR-04 | QO-07 | Allocation control | Process Control / Poka-Yoke | Allocation tests |
| CR-06 | QO-04 | Error Logs | Monitoring | Error-log test |
| CR-07 | QO-06 | Bug Tracker | Fact-Based Decision Making | Bug tracker test |
| CR-08 | QO-05 | Module Tests | Quality Control | Test suite |
| CR-09 | QO-09 | Audit Logs | Traceability | Audit verification |

The matrix will be expanded as additional functional requirements and test cases are implemented.

## Test Evidence Update (Batch 11)

| Customer Req. | Test Evidence now in repository |
|---|---|
| CR-01 | `tests/test_validation.py` |
| CR-04 | `tests/test_allocation.py` |
| CR-07 | `tests/test_bug.py` |
| CR-08 | Full suite: 114 tests passing (Batch 15) |
| CR-06 | `tests/test_logging.py` (error-log fields, sequential IDs, never raises) |
| CR-09 | `tests/test_logging.py` (audit-log fields, append-only, never raises) |

## Hosteller Requirements (Batch 15)

| Customer Req. | Software Feature | Test Evidence |
|---|---|---|
| CR-11 | Complaint categories incl. Food, Maintenance, Washroom | `tests/test_complaint.py`, `tests/test_leave.py::test_washroom_complaint_category_accepted` |
| CR-12 | Allotment list export (CSV) | `tests/test_leave.py` (export tests) |
| CR-13 | Leave Tracking (leave requires an active room) | `tests/test_leave.py` |

Quality Objective IDs for CR-11 to CR-13 are not yet defined.
