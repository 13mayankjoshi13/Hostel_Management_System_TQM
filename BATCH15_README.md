# Batch 15 — Hosteller Feedback Features

From the 28/09/2026 hosteller interview:
- Leave Tracking (new table, service, screen, sidebar item): records which student is on leave and from which room; requires an active allocation; one open leave per student; On Leave → Returned.
- Room allotment list: "Export List (CSV)" on the Allocation screen.
- Complaints: new "Washroom" category (Food and Maintenance already existed).
- Docs appended/updated: `TQM/customer_requirements.md` (CR-11 to CR-13), `TQM/requirements_traceability.md`, `docs/testing.md`, `README.md`, `AI_CONTEXT_HANDOFF.md`. Replace earlier copies; customer_requirements.md keeps all original text.

Tests: 114 pass. Not verified: new screens visually (no tkinter in build environment). Existing databases get the `leaves` table automatically on next start.
