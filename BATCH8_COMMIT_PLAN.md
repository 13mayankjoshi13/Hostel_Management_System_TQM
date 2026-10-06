# Commit Plan — Quality Monitoring + SQC Automation (Batch 8)

```bash
git add app/services/quality_service.py
git commit -m "feat: add quality monitoring data-prep service (Pareto + Fishbone)"
git push

git add app/screens/quality_screen.py
git commit -m "feat: add Quality Monitoring screen with Canvas-drawn Pareto chart and Fishbone diagram"
git push

git add app/screens/main_window.py
git commit -m "feat: add Quality Monitoring to sidebar; enlarge window to fit both charts"
git push

git add tests/test_quality.py
git commit -m "test: add tests for quality monitoring data prep, including empty-data path"
git push

git add BATCH8_README.md BATCH8_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add batch 8 README, commit plan, and updated AI context handoff"
git push
```

## What to Test Before Each Push

| Commit | Test before pushing |
|---|---|
| Quality service | `python -m unittest tests.test_quality -v` |
| Screen | `python run.py` — visit Quality Monitoring with zero bugs logged, confirm the honest "no bugs logged yet" message shows on the Pareto chart and the Fishbone diagram still draws its spine/branches cleanly |
| With data | Log 4–5 bugs across different categories via the Bug Tracker, revisit Quality Monitoring, confirm the Pareto bars and cumulative line look right and all six Fishbone branch labels are visible (not clipped) |
| Full suite | `python -m unittest discover -s tests -v` — all 69 pass |

## Running Total

This batch contributes **5 commits**, bringing the project total to
**~49 commits**.

## What's Left

- **PDCA documentation** — tie a real recurring issue (once you have
  one) to a written Plan-Do-Check-Act cycle in `TQM/PDCA.md`. This is
  authored analysis, not something to auto-generate from code.
- **Final documentation pass** — replace "planned/pending" placeholders
  in `docs/testing.md` and `TQM/requirements_traceability.md` with real
  results now that the app has real test and defect data behind it.
- **Authentication/roles**, if you want audit/error logs to show real
  usernames instead of the current hard-coded `system_admin`.
