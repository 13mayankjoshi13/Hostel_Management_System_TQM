# PDCA Continuous Improvement

## PLAN

- Identify quality problem.
- Define measurable objective.
- Select relevant TQM tool.
- Plan corrective action.

## DO

- Implement the change.
- Record errors and defects.
- Run module and integration tests.

## CHECK

- Compare actual results with the defined quality objective.
- Review defect and error records.
- Check whether the corrective action worked.

## ACT

- Standardize successful improvements.
- Update process controls.
- Update tests and documentation.
- Begin the next improvement cycle.

## Example

Problem → Repeated allocation validation failure

Plan → Review validation rules

Do → Improve validation

Check → Run allocation test suite

Act → Keep corrected validation as the standard and update documentation

## Recorded Improvement Cycles (from project history)

Only cycles that actually occurred during development are listed. Quantitative before/after defect counts are **not yet measured**.

| # | Plan (problem) | Do | Check | Act (standard adopted) |
|---|---|---|---|---|
| 1 | Test runs wrote fake rows into the real evidence CSVs (`TQM/data`) | Redirected DB and log CSV paths to temp files in every test `setUp`/`tearDown` | Real CSVs unchanged after a full test run | Every new test module uses the same isolation pattern |
| 2 | Fishbone diagram clipped on screen (Quality Monitoring) | Read the real canvas size; reschedule drawing until laid out instead of using a guessed minimum | Screenshot confirmed the full diagram is visible | Never substitute guessed canvas sizes; verify UI by screenshot |
| 3 | Bugs could be marked fixed without evidence | Forward-only bug pipeline; "Fixed" requires root cause, corrective action and test case | Bug tests cover the pipeline and rejection of missing evidence | Pipeline enforced in `bug_service`, not the UI |
| 4 | Default administrator password was fixed and unchangeable; deleting accounts could lock everyone out | Added change-password and delete-user with self-delete and last-Administrator guards (Batch 10) | Covered by user-management tests in `tests/test_auth.py` | Guards run before any write |

## Open Items

- Collect real defect counts (found / fixed / repeated) from the Bug Tracker before claiming improvement.
- Error-log and audit-log field tests added in Batch 12 (`tests/test_logging.py`).
