"""Student front page: attendance, fines due, notices, warden, emergency numbers and events."""
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from app.services import fine_service, home_service
from app.utils import session
from app.theme import COLORS, Card, ScrollFrame, _round_rect, chip, kpi_row, make_clickable, show_detail_dialog


def _greeting() -> str:
    hour = datetime.now().hour
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"


class StudentHomeScreen(tk.Frame):
    def __init__(self, parent, fonts, navigate=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._navigate = navigate or (lambda key: None)
        self._banner_text = ("", "")
        self.banner = tk.Canvas(self, height=118, bg=COLORS["background"], highlightthickness=0, bd=0)
        self.banner.pack(fill="x", padx=24, pady=(8, 0))
        self.banner.bind("<Configure>", lambda e: self._draw_banner())
        self.scroll = ScrollFrame(self, bg=COLORS["background"])
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(14, 14))

    def _draw_banner(self):
        c = self.banner
        w = max(c.winfo_width(), 200)
        c.delete("all")
        _round_rect(c, 1, 1, w - 2, 116, 18, fill=COLORS["hero"], outline="")
        for cx, cy, r, col in ((w - 95, 59, 44, COLORS["hero_alt"]), (w - 175, 78, 26, COLORS["hero_alt2"]),
                                (w - 45, 28, 18, COLORS["hero_alt2"])):
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="")
        title, sub = self._banner_text
        c.create_text(26, 40, anchor="w", text=title, fill="#FFFFFF", font=self.fonts["hero"])
        c.create_text(26, 72, anchor="w", text=sub, fill=COLORS["hero_text"], font=self.fonts["body"])
        c.create_text(26, 96, anchor="w", text=date.today().strftime("%A, %d %B %Y"),
                      fill=COLORS["hero_text2"], font=self.fonts["label"])

    def _card(self, parent, title, row, col, span=1, on_click=None):
        card = Card(parent, fit=True)
        card.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=6, pady=6)
        top = tk.Frame(card.body, bg=COLORS["surface"])
        top.pack(fill="x", pady=(0, 6))
        tk.Label(top, text=title, bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                 font=self.fonts["small_bold"]).pack(side="left")
        if on_click:
            arrow = tk.Label(top, text="›", bg=COLORS["surface"], fg=COLORS["accent"],
                             font=self.fonts["body_bold"], cursor="hand2")
            arrow.pack(side="right")
            top.bind("<Button-1>", lambda e: on_click())
        return card.body

    def _line(self, parent, text, font=None, fg=None, wrap=0):
        tk.Label(parent, text=text, bg=COLORS["surface"], fg=fg or COLORS["text_secondary"],
                 font=font or self.fonts["body"], wraplength=wrap, justify="left", anchor="w").pack(anchor="w")

    def refresh(self):
        if session.get_role() != "Student" or session.get_student_id() is None:
            return
        data = home_service.student_home()
        room = data["room"]
        where = f"Room {room['room_number']} · floor {room['floor']}" if room else "No room allocated yet"
        self._banner_text = (f"{_greeting()}, {data['name'].split()[0]}", where)
        self._draw_banner()

        inner = self.scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        att = data["attendance"]
        due = data["fines_due_paise"]
        kpi_row(inner, [
            ("Present (30 days)", str(att["Present"]), "users", COLORS["success"], COLORS["success_soft"],
             lambda: self._navigate("MyLeave")),
            ("Absent (30 days)", str(att["Absent"]), "chat", COLORS["pink"], COLORS["pink_soft"],
             lambda: self._navigate("MyLeave")),
            ("Leave days (30 days)", str(att["Leave"]), "plane", COLORS["info"], COLORS["info_soft"],
             lambda: self._navigate("MyLeave")),
            ("Fines due", fine_service.format_rupees(due), "clipboard", COLORS["orange"], COLORS["orange_soft"],
             lambda: self._navigate("MyFines")),
        ], self.fonts).pack(fill="x", pady=(0, 6))

        # DAILY HOSTEL SCHEDULE & TIMINGS
        timings = data.get("timings") or {}
        ret_status = data.get("return_status") or {}
        is_out = ret_status.get("is_out", False)

        sched_card = Card(inner, fit=True)
        sched_card.pack(fill="x", padx=6, pady=(0, 10))

        # Top Bar of Schedule Card
        top_bar = tk.Frame(sched_card.body, bg=COLORS["surface"])
        top_bar.pack(fill="x", pady=(0, 10))

        title_box = tk.Frame(top_bar, bg=COLORS["surface"])
        title_box.pack(side="left")
        tk.Label(title_box, text="DAILY HOSTEL SCHEDULE & TIMINGS", bg=COLORS["surface"],
                 fg=COLORS["text_primary"], font=self.fonts["section_title"]).pack(anchor="w")
        tk.Label(title_box, text="Official timings for mess, college hours, outing window and gate curfew",
                 bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w")

        right_actions = tk.Frame(top_bar, bg=COLORS["surface"])
        right_actions.pack(side="right")

        # Live Return Status Badge
        badge_bg = COLORS["pink_soft"] if is_out else COLORS["success_soft"]
        badge_fg = COLORS["pink"] if is_out else COLORS["success"]
        badge_txt = "🔴 OUT ON LEAVE" if is_out else "🟢 IN HOSTEL"
        tk.Label(right_actions, text=badge_txt, bg=badge_bg, fg=badge_fg,
                 font=self.fonts["small_bold"], padx=10, pady=4).pack(side="left", padx=(0, 8))

        if session.get_role() in session.ADMIN_ROLES:
            edit_btn = ttk.Button(right_actions, text="✏ Edit Timings", style="Secondary.TButton",
                                  command=self._open_timing_editor)
            edit_btn.pack(side="left")

        # 4 Timings Cards in a responsive grid
        t_grid = tk.Frame(sched_card.body, bg=COLORS["surface"])
        t_grid.pack(fill="x")
        for c in range(4):
            t_grid.columnconfigure(c, weight=1, uniform="timing_col")

        # 1. Mess Timing
        m_box = tk.Frame(t_grid, bg=COLORS["background"], padx=12, pady=10, cursor="hand2")
        m_box.grid(row=0, column=0, sticky="nsew", padx=4, pady=2)
        tk.Label(m_box, text="🍽 MESS TIMINGS", bg=COLORS["background"], fg=COLORS["accent"],
                 font=self.fonts["small_bold"]).pack(anchor="w")
        tk.Label(m_box, text=f"Breakfast: {timings.get('mess_breakfast', '07:30 AM – 09:30 AM')}",
                 bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=(4, 1))
        tk.Label(m_box, text=f"Lunch: {timings.get('mess_lunch', '12:30 PM – 02:30 PM')}",
                 bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=1)
        tk.Label(m_box, text=f"Snacks: {timings.get('mess_snacks', '05:00 PM – 06:00 PM')}",
                 bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=1)
        tk.Label(m_box, text=f"Dinner: {timings.get('mess_dinner', '07:30 PM – 09:30 PM')}",
                 bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=1)

        def _open_mess_details():
            show_detail_dialog(
                parent=self,
                title="Hostel Mess Schedule",
                subtitle="Daily Dining & Meal Timings",
                icon="clipboard",
                color=COLORS["accent"],
                fields=[
                    ("Breakfast", timings.get("mess_breakfast", "07:30 AM – 09:30 AM")),
                    ("Lunch", timings.get("mess_lunch", "12:30 PM – 02:30 PM")),
                    ("Evening Snacks", timings.get("mess_snacks", "05:00 PM – 06:00 PM")),
                    ("Dinner", timings.get("mess_dinner", "07:30 PM – 09:30 PM")),
                    ("Policy", "Students must adhere to dining timings. Meal services close promptly after the listed hours."),
                ]
            )
        make_clickable(m_box, _open_mess_details)

        # 2. College Timing
        c_box = tk.Frame(t_grid, bg=COLORS["background"], padx=12, pady=10, cursor="hand2")
        c_box.grid(row=0, column=1, sticky="nsew", padx=4, pady=2)
        tk.Label(c_box, text="🎓 COLLEGE HOURS", bg=COLORS["background"], fg=COLORS["teal"],
                 font=self.fonts["small_bold"]).pack(anchor="w")
        tk.Label(c_box, text=timings.get("college", "09:00 AM – 05:00 PM (Mon–Fri)"),
                 bg=COLORS["background"], fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w", pady=(6, 2))
        tk.Label(c_box, text="Academic session hours", bg=COLORS["background"],
                 fg=COLORS["text_tertiary"], font=self.fonts["small"]).pack(anchor="w")
        tk.Label(c_box, text="Regular university schedule", bg=COLORS["background"],
                 fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=(4, 0))

        def _open_college_details():
            show_detail_dialog(
                parent=self,
                title="College Academic Hours",
                subtitle="University & Lecture Timings",
                icon="calendar",
                color=COLORS["teal"],
                fields=[
                    ("Class Schedule", timings.get("college", "09:00 AM – 05:00 PM (Mon–Fri)")),
                    ("Attendance Rule", "Minimum 75% attendance required in all registered courses."),
                    ("Guidelines", "Hostellers must be attending lectures during college hours unless granted medical or official leave."),
                ]
            )
        make_clickable(c_box, _open_college_details)

        # 3. Outing Timing
        o_box = tk.Frame(t_grid, bg=COLORS["background"], padx=12, pady=10, cursor="hand2")
        o_box.grid(row=0, column=2, sticky="nsew", padx=4, pady=2)
        tk.Label(o_box, text="🚶 OUTING PERMITTED", bg=COLORS["background"], fg=COLORS["info"],
                 font=self.fonts["small_bold"]).pack(anchor="w")
        tk.Label(o_box, text=timings.get("outing", "05:00 PM – 08:30 PM (Daily)"),
                 bg=COLORS["background"], fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w", pady=(6, 2))
        tk.Label(o_box, text="General outing window", bg=COLORS["background"],
                 fg=COLORS["text_tertiary"], font=self.fonts["small"]).pack(anchor="w")
        tk.Label(o_box, text="Return before night curfew", bg=COLORS["background"],
                 fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=(4, 0))

        def _open_outing_details():
            show_detail_dialog(
                parent=self,
                title="Hostel Outing Policy",
                subtitle="General Outing & Movement Hours",
                icon="plane",
                color=COLORS["info"],
                fields=[
                    ("Permitted Window", timings.get("outing", "05:00 PM – 08:30 PM (Daily)")),
                    ("Entry Requirements", "Valid biometric or physical ID check at main gate upon departure and arrival."),
                    ("Regulations", "Hostellers must return prior to night curfew. Unapproved delays will result in disciplinary action."),
                ]
            )
        make_clickable(o_box, _open_outing_details)

        # 4. Returning Timing & Live Status
        r_box = tk.Frame(t_grid, bg=COLORS["background"], padx=12, pady=10, cursor="hand2")
        r_box.grid(row=0, column=3, sticky="nsew", padx=4, pady=2)
        tk.Label(r_box, text="⏱ RETURNING / CURFEW", bg=COLORS["background"],
                 fg=COLORS["pink"] if is_out else COLORS["orange"],
                 font=self.fonts["small_bold"]).pack(anchor="w")
        tk.Label(r_box, text=timings.get("returning", "08:30 PM (Strict In-Time)"),
                 bg=COLORS["background"], fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w", pady=(6, 2))
        if is_out:
            tk.Label(r_box, text=f"🔴 Return by: {ret_status.get('to_date')}",
                     bg=COLORS["background"], fg=COLORS["pink"], font=self.fonts["small_bold"]).pack(anchor="w")
            tk.Label(r_box, text=f"Reason: {str(ret_status.get('reason', ''))[:26]}",
                     bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w")
        else:
            tk.Label(r_box, text="🟢 Currently in hostel", bg=COLORS["background"],
                     fg=COLORS["success"], font=self.fonts["small_bold"]).pack(anchor="w")
            tk.Label(r_box, text="Main gate closes at curfew", bg=COLORS["background"],
                     fg=COLORS["text_tertiary"], font=self.fonts["small"]).pack(anchor="w")

        def _open_returning_details():
            cur_fields = [
                ("Gate In-Time / Curfew", timings.get("returning", "08:30 PM (Strict Gate In-Time)")),
                ("Current Status", "OUT ON LEAVE" if is_out else "INSIDE HOSTEL"),
            ]
            if is_out:
                cur_fields.extend([
                    ("Leave From", str(ret_status.get("from_date"))),
                    ("Expected Return Date", str(ret_status.get("to_date"))),
                    ("Leave Reason", str(ret_status.get("reason"))),
                    ("Check-in Requirement", "Hosteller must report to the Warden / Hostel Office upon arrival to record official return."),
                ])
            else:
                cur_fields.append(("Notice", "Strict entry deadline. Students returning after gate curfew require written warden clearance."))
            show_detail_dialog(
                parent=self,
                title="Hostel Returning & Curfew Policy",
                subtitle="Gate Timings & Hosteller Live Status",
                icon="key",
                color=COLORS["pink"] if is_out else COLORS["orange"],
                fields=cur_fields
            )
        make_clickable(r_box, _open_returning_details)

        grid = tk.Frame(inner, bg=COLORS["background"])
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1, uniform="c")
        grid.columnconfigure(1, weight=1, uniform="c")

        # RECENT NOTICES
        body = self._card(grid, "RECENT NOTICES", 0, 0, on_click=lambda: self._navigate("MyNotices"))
        if not data["notices"]:
            self._line(body, "No notices yet.", fg=COLORS["text_tertiary"])
        for n in data["notices"]:
            item_box = tk.Frame(body, bg=COLORS["surface"], cursor="hand2")
            item_box.pack(fill="x", pady=(4, 6))
            tk.Label(item_box, text=n["title"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["body_bold"], wraplength=330, justify="left", anchor="w").pack(anchor="w")
            tk.Label(item_box, text=f"{n['created_by']} · {n['created_at']}", bg=COLORS["surface"],
                     fg=COLORS["text_tertiary"], font=self.fonts["small"], anchor="w").pack(anchor="w")
            preview = n["body"][:120] + ("…" if len(n["body"]) > 120 else "")
            tk.Label(item_box, text=preview, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["body"], wraplength=330, justify="left", anchor="w").pack(anchor="w")

            def handle_notice_click(notice=n):
                show_detail_dialog(
                    self, notice["title"], f"Posted by {notice['created_by']} on {notice['created_at']}",
                    "chat", COLORS["accent"],
                    [("Notice Title", notice["title"]),
                     ("Posted By", notice["created_by"]),
                     ("Date & Time", notice["created_at"]),
                     ("Full Content", notice["body"])],
                    action_btn_text="Open in My Notices",
                    on_action=lambda: self._navigate("MyNotices")
                )

            make_clickable(item_box, handle_notice_click)

        # MY FINES
        body = self._card(grid, "MY FINES", 0, 1, on_click=lambda: self._navigate("MyFines"))
        if not data["fines_due"]:
            self._line(body, "No fines due.", fg=COLORS["success"])
        for f in data["fines_due"]:
            f_row = tk.Frame(body, bg=COLORS["surface"], cursor="hand2")
            f_row.pack(fill="x", pady=2)
            tk.Label(f_row, text=f"{f['amount']} — {f['reason']}", bg=COLORS["surface"],
                     fg=COLORS["text_primary"], font=self.fonts["body"], wraplength=330, anchor="w").pack(anchor="w")
            make_clickable(f_row, lambda: self._navigate("MyFines"))
        if data["fines_due"]:
            pay_lbl = tk.Label(body, text="Pay in My Fines ›", bg=COLORS["surface"], fg=COLORS["accent"], cursor="hand2",
                               font=self.fonts["body_bold"])
            pay_lbl.pack(anchor="w", pady=(6, 0))
            pay_lbl.bind("<Button-1>", lambda e: self._navigate("MyFines"))

        # MY WARDEN
        body = self._card(grid, "MY WARDEN", 1, 0, on_click=lambda: self._navigate("Contacts"))
        w = data["warden"]
        if w:
            w_box = tk.Frame(body, bg=COLORS["surface"], cursor="hand2")
            w_box.pack(fill="x")
            tk.Label(w_box, text=w["name"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["body_bold"]).pack(anchor="w")
            tk.Label(w_box, text=f"{w['hostel_name']} · {w['contact_number']}", bg=COLORS["surface"],
                     fg=COLORS["text_secondary"], font=self.fonts["body"]).pack(anchor="w")
            if w["office_hours"]:
                tk.Label(w_box, text=f"Office hours: {w['office_hours']}", bg=COLORS["surface"],
                         fg=COLORS["text_tertiary"], font=self.fonts["label"]).pack(anchor="w")
            make_clickable(w_box, lambda: self._navigate("Contacts"))
        else:
            self._line(body, "No warden assigned yet. Ask the hostel office." if data["gender"] else
                       "Your gender is not set yet, so a warden cannot be shown. Ask the hostel office.",
                       fg=COLORS["text_tertiary"], wrap=330)

        # UPCOMING EVENTS
        body = self._card(grid, "UPCOMING EVENTS", 1, 1, on_click=lambda: self._navigate("Events"))
        if not data["events"]:
            self._line(body, "Nothing coming up.", fg=COLORS["text_tertiary"])
        for e in data["events"]:
            row = tk.Frame(body, bg=COLORS["surface"], cursor="hand2")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=e["event_date"], bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                     font=self.fonts["label"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=e["title"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["body"]).pack(side="left")

            def handle_event_click(ev=e):
                show_detail_dialog(
                    self, ev["title"], f"Hostel Event · {ev['event_date']}", "calendar", COLORS["teal"],
                    [("Title", ev["title"]),
                     ("Date", ev["event_date"])],
                    action_btn_text="Open in Events",
                    on_action=lambda: self._navigate("Events")
                )

            make_clickable(row, handle_event_click)

        # EMERGENCY NUMBERS
        body = self._card(grid, "EMERGENCY NUMBERS", 2, 0, span=2, on_click=lambda: self._navigate("Contacts"))
        flow = tk.Frame(body, bg=COLORS["surface"])
        flow.pack(fill="x")
        for i, c in enumerate(data["emergency"]):
            cell = tk.Frame(flow, bg=COLORS["accent_soft"], padx=10, pady=6, cursor="hand2")
            cell.grid(row=i // 4, column=i % 4, sticky="ew", padx=4, pady=4)
            flow.columnconfigure(i % 4, weight=1, uniform="e")
            tk.Label(cell, text=c["number"], bg=COLORS["accent_soft"], fg=COLORS["accent"],
                     font=self.fonts["body_bold"]).pack(anchor="w")
            tk.Label(cell, text=c["name"], bg=COLORS["accent_soft"], fg=COLORS["text_secondary"],
                     font=self.fonts["small"]).pack(anchor="w")
            make_clickable(cell, lambda: self._navigate("Contacts"))
        self.scroll.update_scroll()

    def _open_timing_editor(self):
        """Administrative editor dialog for hostel timings."""
        from app.services import timing_service
        from app.utils.validation import ValidationError

        current = timing_service.get_timings()
        dlg = tk.Toplevel(self.winfo_toplevel())
        dlg.title("Edit Hostel Timings & Schedule")
        dlg.configure(bg=COLORS["surface"])
        dlg.resizable(False, False)
        try:
            dlg.transient(self.winfo_toplevel())
        except Exception:
            pass

        head = tk.Frame(dlg, bg=COLORS["background"], padx=20, pady=16)
        head.pack(fill="x")
        tk.Label(head, text="Edit Daily Hostel Schedule", bg=COLORS["background"],
                 fg=COLORS["text_primary"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(head, text="Update mess hours, college timings, outing window and night gate curfew.",
                 bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(dlg, bg=COLORS["surface"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        entries = {}
        fields = [
            ("mess_breakfast", "Mess: Breakfast", "e.g. 07:30 AM – 09:30 AM"),
            ("mess_lunch", "Mess: Lunch", "e.g. 12:30 PM – 02:30 PM"),
            ("mess_snacks", "Mess: Evening Snacks", "e.g. 05:00 PM – 06:00 PM"),
            ("mess_dinner", "Mess: Dinner", "e.g. 07:30 PM – 09:30 PM"),
            ("college", "College Timings", "e.g. 09:00 AM – 05:00 PM (Mon–Fri)"),
            ("outing", "Outing Permitted", "e.g. 05:00 PM – 08:30 PM (Daily)"),
            ("returning", "Gate Curfew / In-Time", "e.g. 08:30 PM (Strict Gate In-Time)"),
        ]

        for key, label, hint in fields:
            row = tk.Frame(body, bg=COLORS["surface"], pady=4)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["body_bold"], width=22, anchor="w").pack(side="left")
            var = tk.StringVar(value=current.get(key, ""))
            entries[key] = var
            ent = ttk.Entry(row, textvariable=var, width=32)
            ent.pack(side="left", padx=(8, 8))
            tk.Label(row, text=hint, bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                     font=self.fonts["small"]).pack(side="left")

        foot = tk.Frame(dlg, bg=COLORS["surface"], padx=24, pady=14)
        foot.pack(fill="x")

        def save_changes():
            try:
                new_data = {k: v.get().strip() for k, v in entries.items()}
                timing_service.save_timings(new_data)
                dlg.destroy()
                self.refresh()
                messagebox.showinfo("Success", "Hostel schedule and timings updated successfully.")
            except ValidationError as err:
                messagebox.showerror("Validation Error", str(err))
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to save timings: {ex}")

        ttk.Button(foot, text="Cancel", style="Secondary.TButton", command=dlg.destroy).pack(side="right")
        ttk.Button(foot, text="Save Timings", style="Primary.TButton", command=save_changes).pack(side="right", padx=(0, 8))

        try:
            dlg.grab_set()
        except Exception:
            pass
