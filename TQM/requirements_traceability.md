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
| CR-08 | Full suite: 93 tests passing (Batch 10) |
| CR-06 | Not yet covered — error-log test pending |
| CR-09 | Not yet covered — audit verification test pending |
