"""Staff: send a notice to everyone, a hostel, or one student."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import notice_service, student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, form_card, build_panel, build_table, split_layout, button_row

_AUDIENCES = {
    "All Accounts": "All",
    "All Accounts (Everyone)": "All",
    "Selected Students": "Selected",
    "Selected Students (Multiple)": "Selected",
    "Single Student": "Student",
    "One student": "Student",
    "Boys Hostel": "Boys",
    "Boys hostel": "Boys",
    "Girls Hostel": "Girls",
    "Girls hostel": "Girls",
    "Everyone": "All",
}
_DISPLAY_AUDIENCES = ["All Accounts", "Selected Students", "Single Student", "Boys Hostel", "Girls Hostel"]


class NoticeScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._students = {}
        self._student_display_list = []
        self._selected_student_ids = set()
        self._notices = {}

        section_header(self, "Notices", "Send announcements to all accounts, selected students, or a hostel.", fonts)
        self.left, self.right = split_layout(self)
        form = form_card(self.left, "New notice", fonts)
        self.title_var = tk.StringVar()
        self.audience_var = tk.StringVar(value="All Accounts")
        self.student_var = tk.StringVar()

        form_row(form, fonts, 0, "Title", ttk.Entry(form, textvariable=self.title_var))

        # Send to Row with dropdown + quick pill buttons
        aud_wrap = tk.Frame(form, bg=COLORS["surface"])
        self.audience_box = ttk.Combobox(aud_wrap, textvariable=self.audience_var,
                                         values=_DISPLAY_AUDIENCES, state="readonly", width=16)
        self.audience_box.pack(side="left", fill="x", expand=True)
        self.audience_box.bind("<<ComboboxSelected>>", self._on_audience_change)

        from app.theme import make_clickable
        self.all_pill = tk.Label(aud_wrap, text="📢 All", bg=COLORS["success_soft"],
                                 fg=COLORS["success"], font=fonts["small_bold"], padx=6, pady=2, cursor="hand2")
        self.all_pill.pack(side="left", padx=(4, 0))
        make_clickable(self.all_pill, lambda: self._set_audience("All Accounts"))

        self.sel_pill = tk.Label(aud_wrap, text="👥 Selected", bg=COLORS["accent_soft"],
                                 fg=COLORS["accent"], font=fonts["small_bold"], padx=6, pady=2, cursor="hand2")
        self.sel_pill.pack(side="left", padx=(4, 0))
        make_clickable(self.sel_pill, lambda: self._set_audience("Selected Students"))
        form_row(form, fonts, 1, "Send to", aud_wrap)

        # Student row with dynamic modes (All Accounts / Selected Students / Single Student)
        self.student_wrap = tk.Frame(form, bg=COLORS["surface"])

        # 1. Single Student Combobox
        self.single_box_frame = tk.Frame(self.student_wrap, bg=COLORS["surface"])
        self.student_box = ttk.Combobox(self.single_box_frame, textvariable=self.student_var, state="readonly", width=28)
        self.student_box.pack(fill="x", expand=True)

        # 2. Multi-Select Students Panel
        self.multi_select_frame = tk.Frame(self.student_wrap, bg=COLORS["surface"])
        
        # Search row
        search_row = tk.Frame(self.multi_select_frame, bg=COLORS["surface"])
        search_row.pack(fill="x", pady=(0, 4))
        tk.Label(search_row, text="🔍", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 font=fonts["small"]).pack(side="left", padx=(0, 4))
        self.student_filter_var = tk.StringVar()
        self.student_filter_entry = ttk.Entry(search_row, textvariable=self.student_filter_var, font=fonts["small"])
        self.student_filter_entry.pack(side="left", fill="x", expand=True)
        self.student_filter_var.trace_add("write", lambda *args: self._filter_students())

        # Listbox with Scrollbar
        lb_wrap = tk.Frame(self.multi_select_frame, bg=COLORS["surface"])
        lb_wrap.pack(fill="x", expand=True)
        self.student_listbox = tk.Listbox(
            lb_wrap, selectmode="multiple", height=5, font=fonts["small"],
            exportselection=False, highlightthickness=1, highlightbackground=COLORS["border"],
            activestyle="none", bg=COLORS["surface"], fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"], selectforeground="#FFFFFF"
        )
        lb_sb = ttk.Scrollbar(lb_wrap, orient="vertical", command=self.student_listbox.yview)
        self.student_listbox.configure(yscrollcommand=lb_sb.set)
        self.student_listbox.pack(side="left", fill="both", expand=True)
        lb_sb.pack(side="right", fill="y")
        self.student_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # Action row
        action_row = tk.Frame(self.multi_select_frame, bg=COLORS["surface"])
        action_row.pack(fill="x", pady=(3, 0))
        sel_all_btn = tk.Label(action_row, text="Select All", bg=COLORS["surface"], fg=COLORS["accent"],
                               font=fonts["small_bold"], cursor="hand2")
        sel_all_btn.pack(side="left", padx=(0, 8))
        make_clickable(sel_all_btn, self._select_all_students)

        clear_btn = tk.Label(action_row, text="Clear", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                             font=fonts["small"], cursor="hand2")
        clear_btn.pack(side="left")
        make_clickable(clear_btn, self._clear_student_selection)

        self.selection_count_label = tk.Label(action_row, text="0 selected", bg=COLORS["surface"],
                                              fg=COLORS["text_tertiary"], font=fonts["small"])
        self.selection_count_label.pack(side="right")

        # Live audience status hint
        self.audience_hint = tk.Label(self.student_wrap, text="📢 Notice will be delivered to ALL accounts (all students & staff).",
                                      bg=COLORS["surface"], fg=COLORS["success"], font=fonts["small"], anchor="w", wraplength=260)
        self.audience_hint.pack(fill="x", pady=(3, 0))
        form_row(form, fonts, 2, "Student(s)", self.student_wrap)

        self.body = tk.Text(form, height=6, width=30, wrap="word", relief="flat", highlightthickness=1,
                            highlightbackground=COLORS["border"], font=fonts["body"])
        form_row(form, fonts, 3, "Message", self.body)

        buttons = button_row(form, 4)
        ttk.Button(buttons, text="Send Notice", style="Primary.TButton", command=self.on_send).pack(side="left")
        ttk.Button(buttons, text="Clear", style="Secondary.TButton", command=self.on_clear).pack(side="left", padx=(8, 0))

        content = build_panel(self.right, "Sent notices", fonts)
        self.tree = build_table(content, ("id", "title", "to", "by", "when"),
                                ("ID", "Title", "To", "By", "Sent"), (45, 210, 130, 90, 130), height=10)
        self.tree.pack(fill="both", expand=True)

        def _on_notice_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            try:
                nid = int(vals[0])
            except (ValueError, TypeError):
                nid = vals[0]
            n_data = self._notices.get(nid)
            body_text = n_data["body"] if n_data else "Notice body."
            from app.theme import show_detail_dialog
            show_detail_dialog(
                self, f"Notice #{vals[0]}", f"Posted by {vals[3]} · {vals[4]}", "clipboard", COLORS["accent"],
                [("Notice ID", str(vals[0])),
                 ("Title", str(vals[1])),
                 ("Target Audience", str(vals[2])),
                 ("Posted By", str(vals[3])),
                 ("Date Posted", str(vals[4])),
                 ("Notice Message", str(body_text))]
            )

        self.tree.bind("<Double-Button-1>", _on_notice_select)
        self.tree.bind("<Return>", _on_notice_select)

        self.delete_button = ttk.Button(content, text="Delete Selected", style="Secondary.TButton",
                                        command=self.on_delete)
        self.delete_button.pack(anchor="e", pady=(10, 0))

    def _set_audience(self, val):
        self.audience_var.set(val)
        self._on_audience_change()

    def _on_audience_change(self, event=None):
        raw = self.audience_var.get()
        aud = _AUDIENCES.get(raw, "All")
        if aud == "Selected":
            self.single_box_frame.pack_forget()
            self.multi_select_frame.pack(fill="x", expand=True, pady=(2, 0))
            self.audience_hint.configure(
                text="👥 Group notice: Delivered to each of the selected students above.",
                fg=COLORS["info"]
            )
        elif aud == "Student":
            self.multi_select_frame.pack_forget()
            self.single_box_frame.pack(fill="x", expand=True)
            self.student_box.configure(state="readonly")
            self.audience_hint.configure(
                text="👤 Direct notice: Delivered exclusively to the selected student account.",
                fg=COLORS["info"]
            )
        else:
            self.single_box_frame.pack_forget()
            self.multi_select_frame.pack_forget()
            self.student_var.set("")
            if aud == "All":
                self.audience_hint.configure(
                    text="📢 Broadcast: Delivered to ALL student & staff accounts across the hostel.",
                    fg=COLORS["success"]
                )
            elif aud == "Boys":
                self.audience_hint.configure(
                    text="🏢 Hostel Notice: Delivered to all resident students in Boys Hostel.",
                    fg=COLORS["accent"]
                )
            elif aud == "Girls":
                self.audience_hint.configure(
                    text="🏢 Hostel Notice: Delivered to all resident students in Girls Hostel.",
                    fg=COLORS["accent"]
                )

    def _filter_students(self):
        query = self.student_filter_var.get().strip().lower()
        self.student_listbox.delete(0, "end")
        self._visible_student_names = [name for name in self._student_display_list if query in name.lower()]
        for idx, name in enumerate(self._visible_student_names):
            self.student_listbox.insert("end", name)
            sid = self._students.get(name)
            if sid in self._selected_student_ids:
                self.student_listbox.selection_set(idx)
        self.selection_count_label.configure(text=f"{len(self._selected_student_ids)} selected")

    def _on_listbox_select(self, event=None):
        curr_indices = set(self.student_listbox.curselection())
        for idx, name in enumerate(self._visible_student_names):
            sid = self._students.get(name)
            if sid is not None:
                if idx in curr_indices:
                    self._selected_student_ids.add(sid)
                else:
                    self._selected_student_ids.discard(sid)
        self.selection_count_label.configure(text=f"{len(self._selected_student_ids)} selected")

    def _select_all_students(self):
        self.student_listbox.selection_set(0, "end")
        for name in self._visible_student_names:
            sid = self._students.get(name)
            if sid is not None:
                self._selected_student_ids.add(sid)
        self.selection_count_label.configure(text=f"{len(self._selected_student_ids)} selected")

    def _clear_student_selection(self):
        self.student_listbox.selection_clear(0, "end")
        self._selected_student_ids.clear()
        self.selection_count_label.configure(text="0 selected")

    def on_clear(self):
        self.title_var.set("")
        self.audience_var.set("All Accounts")
        self.student_var.set("")
        self._clear_student_selection()
        self.student_filter_var.set("")
        self.body.delete("1.0", "end")
        self._on_audience_change()

    def on_send(self):
        try:
            raw_audience = self.audience_var.get()
            audience = _AUDIENCES.get(raw_audience, raw_audience)
            if audience == "Selected":
                sids = list(self._selected_student_ids)
                if not sids:
                    raise ValidationError("Please select at least one student from the list.")
                notice_service.send_notice(self.title_var.get(), self.body.get("1.0", "end"), "Student", sids)
                dest = f"{len(sids)} selected student(s)"
            elif audience == "Student":
                sid = self._students.get(self.student_var.get())
                if not sid:
                    raise ValidationError("Select the student who should get this notice.")
                notice_service.send_notice(self.title_var.get(), self.body.get("1.0", "end"), "Student", sid)
                dest = "the selected student"
            else:
                notice_service.send_notice(self.title_var.get(), self.body.get("1.0", "end"), audience)
                dest = "ALL accounts" if audience == "All" else f"{audience} hostel"

            self.title_var.set("")
            self.body.delete("1.0", "end")
            self._clear_student_selection()
            self.refresh()
            messagebox.showinfo("Sent", f"Notice sent successfully to {dest}.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Notice", "send_notice_ui", e)

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a notice first.")
            return
        try:
            notice_service.delete_notice(self.tree.item(selected[0])["values"][0])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Notice", str(e))
        except Exception as e:
            handle_unexpected_error("Notice", "delete_notice_ui", e)

    def refresh(self):
        self._students = {f"{s['name']} ({s['registration_number']})": s["student_id"]
                          for s in student_service.get_all_students()}
        self._student_display_list = list(self._students.keys())
        self._visible_student_names = list(self._student_display_list)
        self.student_box["values"] = self._student_display_list
        self._filter_students()
        self._on_audience_change()

        for row in self.tree.get_children():
            self.tree.delete(row)
        self._notices = {}
        for n in notice_service.list_notices():
            self._notices[n["notice_id"]] = n
            aud = n["audience"]
            if aud == "All":
                target = "📢 All Accounts"
            elif aud == "Boys":
                target = "🏢 Boys Hostel"
            elif aud == "Girls":
                target = "🏢 Girls Hostel"
            elif aud == "Student":
                sname = n.get("student_name") or f"Student #{n.get('student_id', '—')}"
                target = f"👤 {sname}"
            else:
                target = aud
            self.tree.insert("", "end", values=(n["notice_id"], n["title"], target, n["created_by"], n["created_at"]),
                             tags=("default",))

