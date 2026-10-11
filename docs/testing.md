# Testing Strategy

Testing is a major part of the assigned Q09 — Reduce Bugs quality goal.

## Testing Levels

### Unit / Module Testing

Critical services and validation functions will be tested independently.

### Integration Testing

Interactions between UI, services and database will be tested.

### Negative Testing

Invalid inputs and invalid process conditions will be deliberately tested.

### Regression Testing

Previously fixed defects will be retested after relevant changes.

## Test Record

Each test should record:

- Test ID
- Requirement ID
- Module
- Input
- Expected result
- Actual result
- Status
- Defect ID, if applicable

## Initial Test Areas

| Test Area | Example |
|---|---|
| Validation | Empty required field |
| Student | Duplicate registration number |
| Room | Invalid capacity |
| Allocation | Allocate occupied room |
| Complaint | Invalid complaint status |
| Exception handling | Simulated database failure |
| Error logging | Verify required log fields |
| Bug tracker | Create and resolve a test defect |
| Audit | Verify important action creates audit record |

## Implemented Test Inventory (as of Batch 10)

Run: `python -m unittest discover -s tests -t .` — 93 tests, all passing at this point.

| Test module | Tests | Covers |
|---|---|---|
| `test_validation.py` | 22 | Input validators |
| `test_allocation.py` | 9 | Allocation rules |
| `test_complaint.py` | 14 | Complaint rules and status pipeline |
| `test_bug.py` | 17 | Bug logging and status pipeline |
| `test_quality.py` | 7 | Quality monitoring calculations |
| `test_auth.py` | 24 | Hashing, login, roles, user management |

## Known Gaps

- No dedicated tests yet for error-log and audit-log record fields.
- No integration tests across UI, services and database.
- Test IDs and Actual-result records (see Test Record above) are not yet maintained per test; actual results are not yet measured beyond pass/fail.
