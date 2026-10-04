# Batch 6 — Professional UI Redesign (No New Backend Features)

You asked for a redesign that looks human-designed and mature — not an
"AI dashboard." This batch is a full visual and layout rebuild on that
brief. No service, validation, or database logic changed. Same 45 tests.

## Design Decisions

| Instruction | What was done |
|---|---|
| Restrained palette, one accent | Near-white background (`#FAFAFA`), white surfaces, one muted blue accent (`#3457D5`) used only for primary buttons, active nav, and links |
| No cards everywhere | Forms are **unboxed** — plain label/field rows with generous spacing, no border. Only data tables sit in a thin-bordered panel, since tables benefit from visual containment |
| No accent stripes / shadows / glow | Dropped the colored top-stripe-card pattern from Batches 3–5 entirely. Flat surfaces, 1px borders only |
| No oversized type | Page titles are 14pt, not 18–26pt. Hierarchy comes from weight and spacing, not size |
| Practical navigation | Back to a **persistent sidebar** (plain text, no icons, no color fills) — more practical for daily use than Batch 5's two-click hub-and-spoke model |
| Subtle hover | Sidebar items and buttons shift to a slightly different shade on hover; nothing glows or animates beyond that |
| Important action priority | Tables (the actual data) are the visually heavier element; forms are lighter-weight since they're secondary to reviewing existing records |

## What Changed

| File | What |
|---|---|
| `app/theme.py` | Fully rewritten. New helpers: `section_header()`, `form_row()`, `build_panel()`, `build_stat_row()`, `style_treeview_status_tags()`, `bind_hover()`. Old helpers (`build_card`, `build_module_tile`, `build_breadcrumb`, `build_stat_card`) are gone — the design language changed enough that they didn't carry over. |
| `app/screens/main_window.py` | Rewritten — persistent plain-text sidebar replaces Batch 5's hub-and-spoke navigation |
| `app/screens/splash_screen.py` | Restyled — no icon/emoji, shorter (1.1s), neutral palette |
| `app/screens/dashboard_screen.py` | Rewritten — plain KPI strip (label/value pairs with thin dividers) instead of colored stat cards; module-tile grid removed since the sidebar now handles navigation |
| `app/screens/student_screen.py`, `room_screen.py`, `allocation_screen.py`, `complaint_screen.py` | Rewritten — unboxed forms, bordered table panel, breadcrumbs removed (sidebar is now always visible so they're redundant) |

## A Rendering Quirk I Chased Down (and Ruled Out)

While verifying this visually, table text looked faintly blue-tinted in
screenshots. I isolated it with pixel-level sampling: the actual text
color is correctly `#18181B` (near-black) — the blue tint was LCD-style
font-antialiasing fringing from the virtual display used for testing,
not a real bug. I still added a defensive fix (`style_treeview_status_tags`
now always applies an explicit `"default"` tag with the correct
foreground to every row) since relying on ttk's base `Treeview` style
foreground alone is known to be unreliable across platforms/Tk builds —
this is good practice regardless of what caused the visual artifact.

## How to Install

**Replace these files:**
`app/theme.py`, `app/screens/main_window.py`, `app/screens/splash_screen.py`,
`app/screens/dashboard_screen.py`, `app/screens/student_screen.py`,
`app/screens/room_screen.py`, `app/screens/allocation_screen.py`,
`app/screens/complaint_screen.py`.

Nothing else changes — services, utils, database, tests all untouched,
included here only so the ZIP is self-contained.

## How to Run / Test

```bash
python run.py
python -m unittest discover -s tests -v   # expect 45 passed
```
