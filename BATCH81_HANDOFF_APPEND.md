
## Update – page strips; summary of Batches 77-81 (append; do not replace the file)

`page_stats.attach(screen, key, fonts)` (called for every screen in `MainWindow._create_screens`) inserts a `StatStrip` after the screen's title and wraps `screen.refresh` so the strip updates with it; providers live in `page_stats.PROVIDERS`. A provider error hides the strip and logs a Low error. `section_header` now draws an icon tile; `split_layout` left column is 400 wide and `button_row` spans both columns.
Batches 77-81 together: gender and floor/hostel on students and rooms with a Boys/Girls allocation rule; notices, attendance, gender-matched wardens, emergency numbers; student home page, hostel map, events; Super Admin/Admin/Warden/Staff/Student menus; Settings with light/dark theme and accent colour, audit log viewer, student data download, Quality Monitoring (Six Sigma, variance, Taguchi, FMEA, SIPOC, Poka-Yoke); summary strips. Suite: 322 tests.
Not verified: Windows rendering (screenshots were taken under Xvfb on Linux; the rupee sign did not show in that font), live Razorpay, the exe release run, real quality figures (need 5+ days of logs).
