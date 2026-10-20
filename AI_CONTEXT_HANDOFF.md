# AI CONTEXT HANDOFF — Hostel Management System (TQM Project)

**How to use this file:** Paste this entire document as your first
message in a new AI conversation (any model) to continue this project
without losing context. Also attach or paste the contents of your
current GitHub repo (or upload the latest ZIP export) so the AI can see
the actual current code, since this file describes the plan and status,
not every line of code.

Last updated: end of **Batch 9** (Authentication & Roles — a required
login gate, real per-user attribution in every log, replacing the
hard-coded `system_admin`).

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
│   ├── theme.py                 — colors, fonts, ttk styles. Current helpers (Batch 6):
│   │                               section_header(), form_row(), build_panel(), build_stat_row(),
│   │                               style_treeview_status_tags(), status_tag(), bind_hover()
│   │                               REWRITTEN in Batch 6 (neutral/white palette, one blue accent —
│   │                               the Batch 5 dark-mode helpers build_card/build_module_tile/
│   │                               build_breadcrumb/build_stat_card no longer exist)
│   │
│   ├── database/
│   │   └── db.py                — SQLite schema: students, rooms, allocations, complaints
│   │
│   ├── services/                — one file per business module
│   │   ├── student_service.py
│   │   ├── room_service.py
│   │   ├── allocation_service.py
│   │   ├── complaint_service.py
│   │   ├── bug_service.py        — Q09 feature #4: Bug Tracker (Batch 7)
│   │   ├── quality_service.py    — Batch 8: read-only Pareto/Fishbone data prep,
│   │   │                             never writes anything, reads real bug records only
│   │   └── auth_service.py       — NEW in Batch 9: create_user(), authenticate(), logout(),
│   │                                 ensure_default_admin() (PBKDF2 password hashing)
│   │
│   ├── screens/                 — RENAMED from app/ui/ in Batch 3; one file per screen
│   │   ├── main_window.py        — REWRITTEN in Batch 6: persistent plain-text sidebar (no icons,
│   │   │                            no breadcrumbs needed). History: Batch 5 was a splash + slim
│   │   │                            topbar + hub-and-spoke nav; Batch 4 was a top navbar; Batch 3
│   │   │                            was a colored sidebar.
│   │   ├── splash_screen.py       — restyled in Batch 6 (minimal, no icon, ~1.1s); first added Batch 5
│   │   ├── dashboard_screen.py    — REWRITTEN in Batch 6: plain KPI strip (label/value + thin dividers)
│   │   │                            + recent-activity table panel. The Batch 5 module-tile grid is GONE
│   │   │                            — the sidebar handles navigation now, so Dashboard is overview-only.
│   │   ├── student_screen.py      — unboxed form + table panel since Batch 6; no go_home/breadcrumb
│   │   │                            (removed — sidebar is always visible, breadcrumb was redundant)
│   │   ├── room_screen.py         — same pattern as student_screen.py
│   │   ├── allocation_screen.py   — same pattern
│   │   ├── complaint_screen.py    — same pattern; description Text box explicitly themed (color
│   │                                 bug first fixed in Batch 5, still correct here)
│   │   ├── bug_screen.py          — Batch 7: log/Start Progress/Mark Fixed/Close Bug UI
│   │   ├── quality_screen.py      — Batch 8: KPI strip + Canvas-drawn Pareto chart +
│   │   │                             Canvas-drawn Fishbone diagram (no charting library used)
│   │   └── login_screen.py        — NEW in Batch 9: modal login (Toplevel), shown after splash,
│   │                                 before the main window's content; closing it is disabled
│   │
│   └── utils/
│       ├── validation.py        — Strict Validation (Q09 feature #2)
│       ├── logging_service.py   — writes TQM/data/error_logs.csv + audit_logs.csv + defect_log.csv;
│       │                           reads WHO via app.utils.session since Batch 9 (not a static constant)
│       ├── exception_handler.py — Exception Handling (Q09 feature #1)
│       └── session.py           — NEW in Batch 9: runtime "who's logged in right now"
│
├── tests/                        — Module Tests (Q09 feature #3)
│   ├── test_validation.py        (22 tests)
│   ├── test_allocation.py        (9 tests)
│   ├── test_complaint.py         (14 tests)
│   ├── test_bug.py               (17 tests, Batch 7)
│   ├── test_quality.py           (7 tests, Batch 8)
│   └── test_auth.py              (16 tests, Batch 9)
│   → 85 tests total, all passing as of Batch 9
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
        ├── defect_log.csv        — REAL rows since Batch 7 (Bug Tracker); append-only, one row per status change
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

**Batch 5 — Full layout + color redesign (no backend changes):**
- Reason: Batch 4 still felt too similar to Batch 3 to the person
  grading/comparing ("just vertical to horizontal") — this batch changes
  the *navigation model* itself, not just colors.
- Added a **splash screen** on launch (`splash_screen.py`) — borderless,
  centered, ~1.6s, app icon/name/tagline + indeterminate progress bar.
- Replaced the top navbar with **hub-and-spoke navigation**: no
  persistent nav list anywhere. The Dashboard has 4 big clickable
  "module tiles" (Students/Rooms/Allocation/Complaints); every other
  screen has a small "🏠 Dashboard" breadcrumb to go back. The top bar is
  now just the brand + a single Home button (redundant safety net, not
  the primary nav mechanism).
- Completely new palette: dark navy (`#0B1120`) background, dark card
  surfaces (`#131C2E`), electric cyan (`#22D3EE`) accent — shares no
  colors with Batch 3 (indigo) or Batch 4 (teal).
- Fixed a real dark-mode bug: the complaint description `Text` widget
  wasn't themed and showed as a jarring white box — now matches the
  dark UI.
- No test changes — same 45 tests, all still passing.

**Batch 6 — Professional UI redesign (no backend changes):**
- Reason: the person wanted it to look "designed by a real
  professional," explicitly NOT like an AI-generated dashboard — no
  neon, no glow, no gradients, no card-for-everything, no oversized
  type, restrained single-accent palette.
- Switched back from Batch 5's hub-and-spoke model to a **persistent
  plain-text sidebar** (judged more practical for daily use — no more
  two-click round trips through a Dashboard hub to switch modules).
- Forms are now **unboxed** (plain label/field rows, no border/card) —
  only data tables sit inside a thin-bordered panel, since tables
  genuinely benefit from visual containment. This was an explicit
  instruction: "avoid making every section a floating card."
- One accent color only (`#3457D5`, a muted blue), used just for
  primary buttons, the active sidebar indicator, and links.
- Page titles are 14pt (was 17–18pt in Batches 4–5) — hierarchy comes
  from weight/spacing, not large type.
- No test changes — same 45 tests, all still passing.

**Rendering-quirk note (ruled out, not a real bug):** while visually
verifying Batch 6, table text looked blue-tinted in screenshots taken
through the virtual display used for testing. Pixel-level sampling
confirmed the actual rendered color was correctly near-black
(`#18181B`) — the tint was LCD-style font-antialiasing fringing from
that specific virtual display, not a real issue. A defensive fix
(`style_treeview_status_tags` always applies an explicit `"default"`
tag to every row) was added anyway, since relying on ttk's base
`Treeview` style foreground alone is known to be unreliable across
different Tk builds/platforms.

**All UI batches (3–6) were visually verified, not just unit-tested:**
screenshots were taken of the actual running app (via a virtual
display) clicking through every screen and completing every workflow,
before each ZIP was shipped. This caught: a missing-DB-initialization
bug in the Batch 3 test harness, clipped splash-screen text in Batch 5
(fixed by widening the window), a scare in Batch 5 where a button
appeared to be missing after a window-resize change (turned out to be a
stale screenshot from a virtual-display restart, re-verified rather
than assumed away), and the Batch 6 font-fringing investigation above.

**Batch 7 — Bug Tracker (Q09 feature #4, the last unbuilt Q09 feature):**
- Status pipeline, forward-only: Open → In Progress → Fixed → Closed
  (`app/services/bug_service.py`: `log_bug()`, `start_progress()`,
  `mark_fixed()`, `close_bug()`). Same prevention-at-source pattern as
  allocations/complaints: can't skip steps, can't go backward.
- **"Fixed" requires a documented root cause, corrective action, and
  test case reference** before it's accepted — validated, not optional.
  This ties the Bug Tracker directly to the FMEA/root-cause side of the
  TQM plan rather than being a bare status toggle.
- `log_defect()` added to `logging_service.py` — writes a **new row**
  to `TQM/data/defect_log.csv` on every create AND every status change
  (append-only, same pattern as error/audit logs), so the CSV holds the
  bug's full history, which is what Pareto/Fishbone analysis will need.
- New `bugs` table in `db.py`. New `bug_screen.py` (log a bug; table
  action buttons: Start Progress / Mark Fixed / Close Bug — the latter
  two use `simpledialog` prompts for the required fields).
- Dashboard gained a 5th stat tile, "Open Bugs" (counts Open + In
  Progress) — a direct, visible readout of the assigned quality goal
  (Q09: Reduce Bugs).
- 17 new tests (62 total). Visually verified end-to-end: logged two
  bugs, ran one through the full pipeline, confirmed status colors
  update correctly and the Dashboard's Recent Activity panel shows the
  real audit trail of every lifecycle event.

**All five Q09 features are now built**: Exception Handling (Batch 1),
Strict Validation (Batch 1), Module Tests (all batches, 69 total),
Error Logs (Batch 1), Bug Tracker (Batch 7).

**Batch 8 — Quality Monitoring + SQC automation:**
- `app/services/quality_service.py` — pure read-only analysis, never
  writes anything: `get_quality_summary()`, `get_pareto_data()`
  (category counts, sorted descending, with cumulative %),
  `get_fishbone_data()` (bug titles bucketed onto the six standard
  fishbone branches via an explicit, documented `CATEGORY_TO_FISHBONE`
  mapping — see the module for the exact mapping and reasoning, since
  a bug's logged Category doesn't map 1:1 onto the six branches).
- `app/screens/quality_screen.py` — KPI strip + a Pareto chart + a
  Fishbone diagram, both drawn directly on a plain `tk.Canvas` (no
  charting library added — `requirements.txt` still needs nothing
  beyond the standard library). With zero bugs logged, both charts show
  an honest empty-state message rather than fabricated example data.
- 7 new tests (69 total), including the empty-data path.
- **Two real bugs caught and fixed while visually verifying this
  batch**, worth knowing about for any future screen with multiple
  stacked sections or custom Canvas drawing:
  1. The window was too short once a KPI strip + two chart panels were
     stacked — same class of fixed-window-height clipping bug noted
     from Batch 5 below. Fixed by enlarging the window.
  2. A fallback-size bug in the Canvas drawing code itself: it used
     `max(canvas.winfo_height(), 280)` to guard against reading the
     size before layout — but the real canvas height (233px) was
     *smaller* than that 280px fallback, so the code confidently drew
     the bottom three Fishbone branch labels past the canvas's actual
     visible area, silently clipping them. Fixed by reading the real
     geometry and rescheduling the draw via `after()` if it isn't ready
     yet, instead of guessing a fallback number that might be wrong in
     either direction.

**Batch 9 — Authentication & Roles:**
- Flow: Splash → **Login (modal, required)** → Dashboard. The main
  window stays `withdraw()`n until `authenticate()` succeeds; closing
  the login window via the OS close button is disabled on purpose
  (`protocol("WM_DELETE_WINDOW", lambda: None)`) since the app isn't
  usable without a session.
- Roles are exactly the stakeholders the project's own customer
  definition names: **Administrator, Warden, Staff** (`validate_role`).
- Passwords: PBKDF2-HMAC-SHA256, 100,000 iterations, random 16-byte
  salt per user, stored as `"<salt_hex>:<hash_hex>"`. Standard-library
  only (`hashlib`) — no new dependency added.
- Login failure shows one generic message regardless of whether the
  username or password was wrong (standard practice, not a bug if it
  looks "unhelpful" — don't change this without a reason).
- `app/utils/session.py` is plain module-level state (not a class/
  singleton) — deliberate, since the app is single-user-per-process (one
  Tkinter window). `logging_service.py` now calls `session.get_user()`
  / `session.get_role()` at log time instead of importing a static
  constant, so every audit/error/defect log entry shows the real
  logged-in user from this batch onward.
- **First-run bootstrap**: `ensure_default_admin()` (called from
  `app/main.py` right after `initialize_database()`) creates one
  default account — `admin` / `admin123` — only if the `users` table is
  empty. Shown as a hint on the login screen itself.
- No user-management screen yet — `create_user()` exists in
  `auth_service.py` but there's no UI for an admin to add Warden/Staff
  accounts or change the default password. Noted as the top item in
  "What's NOT Built" below.
- 16 new tests (85 total).
- **Bug caught and fixed while visually verifying this batch**: same
  class of issue as the Batch 6 splash-screen sizing bug — the login
  window's first size (380×300) clipped both the title and the bottom
  of the form. Fixed by enlarging to 440×380. Re-verified with a full
  login → wrong password → correct password → navigate → logout cycle,
  screenshotted at every step.

**Commit count so far:** ~57 meaningful commits across all batches.

## 5. What's NOT Built Yet (in planned order)

1. **User-management screen** — a UI for `create_user()` so an admin
   can add Warden/Staff accounts and change the default admin password
   without dropping into a Python shell. The service layer already
   supports this; only the screen is missing.
2. **PDCA documentation** — tie a real recurring issue (once one
   exists) to a written Plan-Do-Check-Act cycle in `TQM/PDCA.md`. This
   is authored analysis, not something to auto-generate from code.
3. **Final documentation pass** — updating `docs/testing.md`,
   `TQM/requirements_traceability.md`, etc. with real, non-placeholder
   evidence now that the app has real test, defect, and auth data
   behind it.

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
- **The visual design has been redesigned four times now** (Batch 3
  sidebar/indigo → Batch 4 navbar/teal, judged too similar → Batch 5
  hub-and-spoke/dark, judged still too "AI-dashboard" → Batch 6
  sidebar/neutral-with-one-accent, explicitly asked to look
  "human-designed... not flashy, futuristic, or obviously
  AI-generated"). Batch 6 is the current design language and is a good
  default to extend rather than replace, unless asked again. If asked
  to redesign again: the un-boxed-form + bordered-table-panel +
  single-accent pattern from Batch 6 is deliberately restrained — lean
  further into typography/spacing changes before reaching for a new
  layout paradigm, since sidebar/navbar/hub-and-spoke are now all
  "used up" as distinct navigation models for an app this size.
- **Fixed window sizing is fragile — this has now bitten two batches.**
  Screens use `pack`/`grid` inside a fixed-size
  `place(relwidth=1, relheight=1)` container with no scrollbar. Adding
  any extra vertical content (Batch 5's breadcrumb row; Batch 8's second
  stacked chart panel) can push content below the visible window and
  clip it silently (no error, just an invisible or truncated widget).
  Same bug hit the Batch 9 login window too (a separate fixed-size
  `Toplevel`, 380×300, too small for its own content) — fixed by
  enlarging to 440×380. This has now happened three times (Batch 5,
  Batch 8, Batch 9): **always check a new fixed-size window/Toplevel
  against its actual content via the virtual-display screenshot
  process**, don't assume a size "looks about right."
  Main window size is 1150×820 / minsize 980×680 as of Batch 8. If a
  future batch adds more vertical content to any screen, either
  re-verify visually (virtual display + screenshot — don't skip this)
  or consider adding a scrollable canvas wrapper instead of continuing
  to grow the fixed window size indefinitely.
- **When reading `tk.Canvas` geometry for custom drawing** (as in
  `quality_screen.py`), never guess a fallback minimum size if
  `winfo_width()`/`winfo_height()` return something unexpected —
  Batch 8 had a bug where a "safe-looking" fallback (280px) was actually
  *larger* than the real rendered canvas height (233px), causing content
  to be confidently drawn past the canvas's real visible bounds and
  silently clipped. Instead: if the read-back size is `<= 1` (not yet
  laid out), reschedule the draw with `self.after(50, ...)` and return —
  never substitute a guessed constant.
- **Folder convention:** one folder per file *type* — `services/` holds
  all service files, `screens/` holds all screen/UI files, `utils/`
  holds cross-cutting helpers, `database/` holds the schema/connection
  layer. Don't scatter files by feature instead of by type.

## 7. How to Continue From Here

Tell the new AI: *"Continue from Batch 11 — auth, User Management and PDCA/testing docs are done (100 tests, incl. error/audit log tests from Batch 12); next is a final documentation pass and a visual check of the User Management screen. Here's the current repo/ZIP."* and attach the latest
export of the repository. The AI should:
1. Read this handoff file fully before writing any code.
2. Confirm the current file structure matches section 3 above (ask to
   see the repo/ZIP if not already attached).
3. Follow the working conventions in section 6 for the new batch.
4. Update this `AI_CONTEXT_HANDOFF.md` at the end of the new batch with
   what changed, and include it in the new ZIP.

## 8. Batch 10 — User Management
- `auth_service`: `list_users`, `change_password`, `delete_user` (guards: not own account, not last Administrator).
- `screens/user_screen.py` + admin-only sidebar item "User Management" (hidden for Warden/Staff; `show_screen` also blocks them).
- 8 new tests in `tests/test_auth.py` (93 total passing).
- UI for this batch was NOT screenshot-verified (no tkinter in that build environment) — verify visually first next time.

## 9. Batch 11 — PDCA and documentation
- Appended (never overwrote) to `TQM/PDCA.md`, `docs/testing.md`, `TQM/requirements_traceability.md`.
- Batch 12 added `tests/test_logging.py` (7 tests) closing the CR-06/CR-09 gaps; suite is 100 tests.
- Gaps still open: real defect counts; visual check of the User Management screen; `exception_handler` now covered (Batch 14).
- Next: final portfolio/README pass.

## 10. Batch 13 — README and architecture update
- Appended (never overwrote) "Implementation Status" and "Run" to `README.md`, and "Code Layout" to `docs/architecture.md`.
- Remaining: visual check of User Management, real defect counts, `exception_handler` now covered (Batch 14).

## 11. Batch 14 — Exception handler tests
- `tests/test_exception_handler.py` (2 tests; tkinter stubbed so it runs headless). Suite: 102 tests.
- Remaining: visual check of User Management; real defect counts.

## 12. Batch 15 — Hosteller feedback features
- Source: hosteller interview 28/09/2026 (food/maintenance/washroom complaints, allotment list, leave tracking). Recorded in `TQM/customer_requirements.md` as CR-11 to CR-13.
- New: `leaves` table, `services/leave_service.py`, `screens/leave_screen.py` (sidebar "Leave Tracking"), `allocation_service.export_allocation_list` + "Export List (CSV)" button, "Washroom" complaint category.
- 12 new tests in `tests/test_leave.py`; suite is 114. UI not screenshot-verified (no tkinter in build environment).
- Quality Objective IDs for CR-11 to CR-13 not yet defined.

## 13. Batch 16 — Student side
- New role `Student`; `users.student_id` links an account to a student record (migrated automatically for old databases). Admin creates student accounts in User Management and picks the student.
- `session.get_student_id()`; `authenticate` returns and stores `student_id`.
- `services/student_portal_service.py`: every function takes the student from the session, never from the caller (own-data only; non-student sessions rejected). Screens: `my_room_screen.py`, `my_complaints_screen.py`, `my_leave_screen.py`.
- `main_window._allowed_screens(role)` decides sidebar items and blocks other screens: Student sees only the three portal screens; staff roles never see them.
- 18 new tests in `tests/test_student_portal.py`; suite is 132. UI not screenshot-verified (no tkinter in build environment).
- Known limits: staff-side services are gated by navigation, not re-checked per call; students cannot change their own password yet; deleting a student who has an account is blocked by a database error message.

## 14. Batch 17 — Demo data
- `app/database/seed_demo.py` (`python -m app.database.seed_demo`): 56 students, Block A / Block B double rooms (2 per room, plus empty A201 and B201), a Student login each (`firstname_lastname`, password `Welcome123`), 5 sample complaints, 3 sample leaves. Idempotent.
- Block grouping is an editable column in the `STUDENTS` list. Registration number = `24103020` + roll (Mayank = 37; others assigned alphabetically, so they are guesses). Contacts are made-up Indian-style mobile numbers. Re-running upgrades old `DEMO###` students in place.
- Audit/error entries from seeding go to a throwaway file so `TQM/data` evidence stays clean. Demo complaints/leaves do appear in dashboard counts.
- 8 new tests in `tests/test_seed_demo.py`; suite is 140.

## 15. Batch 18 — UI redesign and calendar
- Restyled all screens after a user-supplied dashboard reference: `app/theme.py` v5 (palette, `Card`, `form_card`, `split_layout`, `kpi_row`, vector icons, `ScrollFrame`), sidebar + top bar in `main_window.py`, new splash/login, dashboard (calendar, quick actions, upcoming, KPI cards, rooms grid/recent activity).
- Calendar: `events` table (Holiday / Hostel Event / Exam), `services/event_service.py` (Administrator/Warden edit only), `screens/calendar_widget.py`, `screens/calendar_screen.py`; 23 default 2026 holidays seeded on first run (Central Government list; may differ from the university's).
- `validation.py`: `validate_event_date/title/kind`. 10 new tests in `tests/test_events.py`; suite is 150.
- Layouts were checked with Xvfb screenshots using bitmap fonts only; Segoe UI look on Windows is unverified. No image files are used.
- Known limits unchanged from section 14, plus: CR-15 has no Quality Objective ID.

## 16. Batches 20-29 — bug fixing and requests
- Bugs BUG-001 to BUG-009 found by exploratory testing, fixed and written up in `docs/bugs/`; `python -m app.database.log_bugs` loads them into the Bug Tracker (idempotent) with Mayank as reporter and fixer. Regression tests in `tests/test_bug_fixes.py`.
- Batch 29: `users.status` (Pending/Active), `register_student`, `approve_user`, Sign-up dialog (`signup_screen.py`); `bugs.reported_by` / `fixed_by` (defect CSV columns unchanged); bug screen filter and detail; Quality screen scrolls and shows people; `update_student`, `get_all_students(sort_by)`, `My Details` screen (`student_portal_service.my_details/update_my_details`).
- Suite is 195 tests. Sign-up verifies registration number plus contact number against an existing student record; students the hostel has not added cannot sign up.
- Known limits: pending/active status is checked only at login; rejecting a request means deleting the account; the defect CSV has no reporter/fixer columns.
## 17. Bug-hunt log (BUG-015 to BUG-035, Q09 Reduce Bugs)
Each bug has `docs/bugs/BUG-0NN.md` (how found, root cause, fix, test), a regression test, and an entry in `app/database/log_bugs.py` (load with `python -m app.database.log_bugs`; Mayank is reporter and fixer; bugs stay "Fixed" until closed in the Bug screen). Latest full suite: 241 tests.

| Bug | Severity | What |
|---|---|---|
| 015 | Low | Sign-up dialog could be submitted twice |
| 016 | Low | Calendar did not jump to a new event's month |
| 017, 019 | Medium | Record IDs `True` / `1.9` accepted (`validate_record_id`) |
| 018 | Medium | Open leave stayed after room release |
| 020 | Medium | CSV formula text in evidence logs |
| 021, 022 | Low | Event date window; duplicate titles ignoring case |
| 023 | High | Roles enforced only in navigation; now `session.require_roles` in services |
| 024 | High | Simultaneous allocations could overfill a room (`BEGIN IMMEDIATE`, unique indexes) |
| 025 | High | Login lockout after 5 wrong passwords (5 minutes) |
| 026 | High | Tk callback errors now logged and shown |
| 027 | High | Start-up failures shown in a window |
| 028, 029 | High | Default `admin/admin123` and seeded `Welcome123` must be changed at first login |
| 030 | High | Registration numbers case-insensitive |
| 031 | Critical | Daily verified backup + restore (`app/database/backup.py`) |
| 032 | High | Users change their own password (sidebar link) |
| 033 | High | 15-minute idle log-out |
| 034 | High | Read-only data health check (`python -m app.database.check_data`) |
| 035 | High | Defect log has reporter/fixer; old log files upgraded; write failures logged |

Conventions added: tests clear the session in `setUp`; any new service function that takes an ID uses `validate_record_id`; any staff-only service starts with `session.require_roles(...)`.

Known gaps: Devanagari names are rejected (scope decision needed); backups sit on the same disk; `hostel.db` and `app/database/backups/` hold real student data and must be gitignored; Segoe UI rendering on Windows unverified; Quality Objective IDs for CR-11 onward undefined.
## Update – BUG-036 to BUG-043 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 036 | High | Student sessions could read all students' complaints, allocations and the allotment export |
| 037 | Medium | Login no longer reveals which usernames exist |
| 038 | High | Sign-up lockout (`signup_attempts`) stops guessing a classmate's contact number |
| 039 | High | Times shown in local time (`app/utils/timefmt.py`), stored in UTC; legacy local-ISO rows converted |
| 040 | High | Log-in window can be closed and the app quit from it |
| 041 | High | Log rows queued in `<log>.csv.pending` while a CSV is locked (Excel) |
| 042 | High | Windows-encoded logs repaired to UTF-8; error ids = highest + 1 |
| 043 | High | Restore requires the hostel tables; failed backups leave no partial file |

Total: 43 bugs found, fixed, regression-tested, logged and written up. Suite: 254 tests (18 UI tests skip without a display).

New conventions: `.pending` files and `hostel.db` must be gitignored; log writers never raise; displayed times go through `timefmt`.

Known gaps unchanged: Devanagari names rejected; backups on the same disk; Windows rendering unverified; no quality results measured yet.

## Update – BUG-046 (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 046 | Medium | `auth_service.change_password` (admin reset) clears lockout and sets `must_change_password` unless it is the administrator's own account |

Total: 46 bugs. Suite: 257 tests (18 UI tests skip without a display).