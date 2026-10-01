# Batch 5 — Full Layout + Color Redesign (No New Backend Features)

You said Batch 4 still felt like "the same thing, just vertical to
horizontal," since other students had copied the general look. This
batch is a genuine structural change — a different navigation model, a
different theme end-to-end, and a new first impression (splash screen).
No service, validation, or database logic changed. Same 45 tests.

## Navigation History (so it's clear what actually changed each time)

| Batch | Navigation | Theme |
|---|---|---|
| 3 | Left sidebar, 5 always-visible nav items | Light, indigo |
| 4 | Top navbar, 5 always-visible nav pills | Light, teal |
| **5 (this one)** | **Splash screen → Dashboard hub with big module tiles → breadcrumb back** | **Dark, electric cyan** |

## What's Different This Time

1. **Splash screen on launch** (`app/screens/splash_screen.py`) — a
   borderless centered window with the app icon, name, tagline, and an
   animated progress bar for ~1.6 seconds before the Dashboard appears.
2. **No persistent nav bar at all.** The top bar is now just the brand
   on the left and a single "🏠 Dashboard" button on the right — nothing
   else is always visible.
3. **Dashboard is a hub, not just a stats page.** Below the live stat
   tiles, there's a new row of 4 big clickable **module tiles**
   (Students / Rooms / Room Allocation / Complaints) with icons and
   descriptions — click one to go there.
4. **Every module screen has a breadcrumb** ("🏠 Dashboard › Students")
   at the top instead of a nav bar — click "Dashboard" to go back.
5. **Completely different palette**: near-black navy background
   (`#0B1120`), dark surface cards (`#131C2E`), electric cyan accent
   (`#22D3EE`) — nothing shared with Batch 3's indigo or Batch 4's teal.

This means: Dashboard → click a tile → Dashboard → click a different
tile. Any screen is reachable from any other screen in exactly two
clicks, without a nav list ever being on screen.

## Files Changed

| File | What |
|---|---|
| `app/theme.py` | Completely rewritten for dark mode; new helpers `build_module_tile()` and `build_breadcrumb()` added |
| `app/screens/splash_screen.py` | **New file** |
| `app/screens/dashboard_screen.py` | Rewritten — added the module-tile grid and a `navigate` callback |
| `app/screens/main_window.py` | Completely rewritten — splash sequence, slim top bar, hub-and-spoke wiring |
| `app/screens/student_screen.py`, `room_screen.py`, `allocation_screen.py` | Small, identical edit to each: accept `go_home` param, add breadcrumb |
| `app/screens/complaint_screen.py` | Same breadcrumb edit, **plus** a real bug fix: the description `Text` box was still rendering as a plain white box in dark mode — now themed correctly |

## Two Real Bugs I Caught and Fixed Before Shipping

I visually verified this batch the same way as the last two (virtual
display, click through every screen, screenshot each step) and it
caught two genuine issues that compiling/testing alone would have
missed:

1. **Splash screen text was clipped** — "Hostel Management System" at
   the first font size/window width I tried didn't fit. Fixed by
   widening the splash window and reducing the font size slightly.
2. **The "Release Selected" button appeared to be missing** on the Room
   Allocation screen after a window-sizing change — turned out to be a
   stale screenshot from a virtual-display restart, not a real bug, but
   I didn't take that on faith — I re-ran the whole verification pass
   and confirmed the button genuinely renders and works before
   packaging this ZIP. (I also trimmed a couple of table heights and
   grew the default window size as a safety margin, since the extra
   breadcrumb row was eating vertical room that line close to the
   window edge.)

## How to Install

1. **Replace**: `app/theme.py`, `app/screens/main_window.py`,
   `app/screens/dashboard_screen.py`, `app/screens/student_screen.py`,
   `app/screens/room_screen.py`, `app/screens/allocation_screen.py`,
   `app/screens/complaint_screen.py`.
2. **Add**: `app/screens/splash_screen.py` (new file).
3. Nothing else changes — services, utils, database, tests all
   untouched, included here only so the ZIP is self-contained.

## How to Run

```bash
python run.py
```

You'll see the splash screen first (~1.6s), then land on the Dashboard.

## How to Test

```bash
python -m unittest discover -s tests -v
```

Expected: **45 passed** — unchanged, since no logic changed.

## If You Want It to Look Different Again

Same as before: everything is in `app/theme.py`'s `COLORS` dict. But if
asked for a "complete change" again, change the **navigation model**
again too, not just the colors — a sidebar, a navbar, and a hub are the
three natural options for an app this size; consider a wizard/stepper
style next if a fourth distinct option is ever needed.
