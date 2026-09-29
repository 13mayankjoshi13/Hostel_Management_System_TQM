# AI CONTEXT HANDOFF — Hostel Management System (TQM Project)

**How to use this file:** Paste this entire document as your first
message in a new AI conversation (any model) to continue this project
without losing context. Also attach or paste the contents of your
current GitHub repo (or upload the latest ZIP export) so the AI can see
the actual current code, since this file describes the plan and status,
not every line of code.

Last updated: end of **Batch 4** (complete UI redesign — top navbar +
Dashboard screen, replacing Batch 3's sidebar look).

---

## 1. Who This Is For

- **Name:** Mayank Joshi
- **Roll No.:** 2410302037
- **Branch:** CSE, Section B
- **Course:** BBAT104 — Fundamentals of TQM
- **Academic Session:** 2026–27
- **Deadline:** Presentation/demo on the **15th** — UI must look
  presentable, not a plain default-Tkinter box.

## 2. The Assignment

- **Assigned project:** Hostel Management System
- **Assigned quality goal:** Q09 — Reduce Bugs
- **The five assigned Q09 quality features (must stay central):**
  1. Exception Handling
  2. Strict Validation
  3. Module Tests
  4. Bug Tracker
  5. Error Logs
- **Primary customer:** Hostel Administration / Hostel Warden (not the
  students — they're users, not the customer)
- **Core philosophy:**
  ```
  Prevent Errors → Control Processes → Detect Errors →
  Record Evidence → Analyze Problems → Improve Process
  ```
- **Hard rule: never fabricate quality evidence.** Metrics/logs start as
  "planned / pending / not yet measured" and only get real values once
  the software actually generates them. FMEA initial ratings are
  planning values, to be updated later from real defect/test evidence.

Full original requirements (customer requirements, FMEA formula, SIPOC,
CTQ, Pareto/Fishbone/PDCA expectations, measurable objectives format)
are preserved verbatim in the original **FULL PROJECT CONTEXT** document
— if the new AI doesn't have it, ask the user to re-paste it; don't
reconstruct it from memory.

## 3. Repository Structure (current, real — not aspirational)

```
Hostel_Management_System-main/          (GitHub repo root — NO "Project
│                                         Guidelines" wrapper folder)
├── README.md
├── run.py
├── requirements.txt
│
├── app/
│   ├── main.py                  — bootstrap: initialize_database() then launch MainWindow
│   ├── config.py                — all paths (DB, CSVs) in one place
│   ├── theme.py                 — colors, fonts, ttk styles, build_card(), build_stat_card()
│   │                               REWRITTEN in Batch 4 (teal/slate palette, accent-stripe cards)
│   │
│   ├── database/
│   │   └── db.py                — SQLite schema: students, rooms, allocations, complaints
│   │
│   ├── services/                — one file per business module
│   │   ├── student_service.py
│   │   ├── room_service.py
│   │   ├── allocation_service.py
│   │   └── complaint_service.py
│   │
│   ├── screens/                 — RENAMED from app/ui/ in Batch 3; one file per screen
│   │   ├── main_window.py        — REWRITTEN in Batch 4: top navbar (was left sidebar), wires navigation only
│   │   ├── dashboard_screen.py    — NEW in Batch 4: landing screen, live stat tiles + recent audit activity
│   │   ├── student_screen.py
│   │   ├── room_screen.py
│   │   ├── allocation_screen.py
│   │   └── complaint_screen.py
│   │
│   └── utils/
│       ├── validation.py        — Strict Validation (Q09 feature #2)
│       ├── logging_service.py   — writes TQM/data/error_logs.csv + audit_logs.csv
│       └── exception_handler.py — Exception Handling (Q09 feature #1)
│
├── tests/                        — Module Tests (Q09 feature #3)
│   ├── test_validation.py        (22 tests)
│   ├── test_allocation.py        (9 tests)
│   └── test_complaint.py         (14 tests)
│   → 45 tests total, all passing as of Batch 3
│
├── docs/                         — normal project documentation (untouched since foundation)
│   ├── project_overview.md, vision.md, mission.md, quality_objectives.md,
│   │   SRS.md, architecture.md, ER_Diagram.md, testing.md
│
└── TQM/                          — TQM evidence (untouched by app batches except data/*.csv contents)
    ├── reference/                 (teacher-provided source-of-truth docs — never edit)
    │   ├── BBAT104_Fundamentals of TQM.docx
    │   ├── BBAT104_TQM_Project_Guidelines_Session_2026_27.docx
    │   └── TQM PROJECT ALLOTMENT.xlsx
    ├── customer_requirements.md, assigned_quality_goal.md, quality_features.md,
    │   software_features_tqm_mapping.md, error_prevention.md, process_control.md,
    │   process_map.md, SIPOC.md, CTQ_Tree.md, FMEA.md, quality_monitoring.md,
    │   Pareto.md, Fishbone.md, PDCA.md, requirements_traceability.md
    └── data/
        ├── audit_logs.csv        — REAL rows written by the app on every create/assign/resolve/allocate/release
        ├── error_logs.csv        — REAL rows written on any caught exception/DB error
        ├── defect_log.csv        — still empty; populated once Bug Tracker (next batch) exists
        ├── checksheet.csv, process_metrics.csv, quality_metrics.csv — not yet automated
```

**IMPORTANT:** `app/ui/` no longer exists — it was renamed to
`app/screens/` in Batch 3 and the old combined `main_window.py` was
split into one file per screen. If you see any reference to `app.ui` in
old code, it's stale.

## 4. What's Actually Implemented (by batch)

**Documentation Foundation** (pre-Batch-1): `docs/` and `TQM/*.md` files,
`TQM/data/*.csv` with headers only, teacher references in
`TQM/reference/`.

**Batch 1 — Application Foundation:**
- SQLite (`students`, `rooms` tables; `allocations` table declared early)
- Strict Validation: name, registration number, contact number, room
  number, room type, capacity
- Central Exception Handler (`app/utils/exception_handler.py`)
- Error/Audit logging to real CSVs
- Tkinter GUI (plain — later restyled in Batch 3)
- 22 module tests

**Batch 2 — Room Allocation:**
- Full prevention pipeline: Select Student → Check Student → Select Room
  → Check Room Exists → Check Capacity → Check Existing Allocation →
  Allocate → Audit
- `release_allocation()` (marks 'Released', doesn't delete — keeps
  history/traceability)
- 9 new tests (31 total at that point)

**Batch 3 — Complaint Management + UI overhaul + restructure:**
- Complaint status pipeline: Open → Assigned → Resolved (or Open →
  Resolved directly); backward/duplicate transitions rejected
- `app/theme.py` + first visual redesign: dark sidebar nav, indigo
  palette, card layout, striped tables, colored status badges (replaces
  plain `ttk.Notebook` white-box tabs)
- `app/ui/` → `app/screens/`, split into one file per screen
- 14 new tests (45 total)

**Batch 4 — Complete UI redesign (no backend changes):**
- Reason: the Batch 3 look had been copied by other students, so this
  batch is a ground-up visual change, not a recolor.
- Layout changed from left sidebar → **top navbar** with pill nav
  buttons.
- Palette changed from indigo → **teal/slate**.
- Cards changed from full grey border boxes → white cards with a thin
  border + **colored top accent stripe**.
- **New Dashboard screen** (`app/screens/dashboard_screen.py`) — now the
  landing screen. Shows 4 live stat tiles (Total Students, Rooms
  Occupied %, Active Allocations, Open Complaints) computed from the
  real service layer, plus a "Recent Activity" panel reading the tail of
  `TQM/data/audit_logs.csv` directly — a visible link between the
  software and the TQM evidence it generates.
- `student_screen.py` / `room_screen.py` / `allocation_screen.py` /
  `complaint_screen.py` were **not edited** — they already read all
  styling from `app/theme.py`, so the new look applied with zero changes
  to those files.
- No test changes — same 45 tests, all still passing (only presentation
  changed).

**Both UI batches were visually verified, not just unit-tested:**
screenshots were taken of the actual running app (via a virtual display)
clicking through every screen and completing every workflow, before
each ZIP was shipped. This caught a real bug in the Batch 3 test
harness (missing DB initialization) before it reached the user.

**Commit count so far:** ~24 meaningful commits across all batches
(course expects 30+; this is on track).

## 5. What's NOT Built Yet (in planned order)

1. **Bug Tracker** (Q09 feature #4) — fields: Bug ID, Date, Module,
   Category, Title, Description, Severity, Priority, Status, Root Cause,
   Corrective Action, Test Case. Writes to `TQM/data/defect_log.csv`.
2. **Quality Monitoring** dashboard pulling real numbers from the CSVs
   that already exist and are being populated.
3. **SQC automation**: Pareto chart and Fishbone diagram generated from
   `defect_log.csv`; PDCA cycle documentation tied to real recurring
   issues found during testing.
4. **Authentication / roles** — currently every audit/error log entry
   is hard-coded to `system_admin` / `Administrator` in `app/config.py`
   (`CURRENT_USER`, `CURRENT_ROLE`). No login screen exists.
5. **Final documentation pass** — updating `docs/testing.md`,
   `TQM/requirements_traceability.md`, etc. with real, non-placeholder
   evidence once the above is done.

## 6. Working Conventions (apply to every future batch)

- **Deliver as a ZIP**, not one file at a time. Every batch ZIP must
  include: complete folder structure for that batch, complete file
  contents (no placeholders where real implementation is expected), a
  `BATCHN_README.md`, a `BATCHN_COMMIT_PLAN.md` with exact
  `git add` / `git commit -m "..."` / `git push` commands (conventional
  commit style: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`), and
  this `AI_CONTEXT_HANDOFF.md` updated to reflect the new state.
- **Never overwrite existing content** in the GitHub README, portfolio,
  or resume when adding new material — append/merge instead.
- **For certain documents** (e.g. an internship withdrawal report, if
  that ever comes up in a different context) — preserve verbatim, no
  consolidation or summarization, including repeated points. (Not
  relevant to this TQM project specifically, but is a standing
  preference — flagging so it's not lost.)
- **Do not fabricate quality results.** If a metric isn't measured yet,
  say "planned" / "pending" / "not yet measured" — never a fake number.
- **Test isolation matters**: every test file must redirect BOTH the
  SQLite path (`app.config.DATABASE_PATH` / `db_module.DATABASE_PATH`)
  AND the logging CSV paths (`app.utils.logging_service.ERROR_LOG_CSV`
  / `AUDIT_LOG_CSV`) to temp files in `setUp`/`tearDown`. This bit us
  twice already (Batches 1 and 2 both initially leaked test rows into
  the real `TQM/data/*.csv` files before being fixed) — don't repeat
  that mistake in new test files.
- **Before shipping a UI batch**, verify it actually renders (a virtual
  display + screenshot check caught real bugs in Batch 3 that
  compile-checking alone missed) rather than shipping unverified GUI
  code.
- **The visual design has already been copied by classmates once**
  (the Batch 3 sidebar/indigo look). If asked to redesign again, make a
  structural change (layout paradigm, not just a color swap) — e.g.
  Batch 4 moved from a left sidebar to a top navbar and added a new
  Dashboard screen. Simply changing `COLORS` values is not enough if
  asked to "change it completely" again.
- **Folder convention:** one folder per file *type* — `services/` holds
  all service files, `screens/` holds all screen/UI files, `utils/`
  holds cross-cutting helpers, `database/` holds the schema/connection
  layer. Don't scatter files by feature instead of by type.

## 7. How to Continue From Here

Tell the new AI: *"Continue from Batch 4 — next is the Bug Tracker
(Q09 feature #4). Here's the current repo/ZIP."* and attach the latest
export of the repository. The AI should:
1. Read this handoff file fully before writing any code.
2. Confirm the current file structure matches section 3 above (ask to
   see the repo/ZIP if not already attached).
3. Follow the working conventions in section 6 for the new batch.
4. Update this `AI_CONTEXT_HANDOFF.md` at the end of the new batch with
   what changed, and include it in the new ZIP.
