"""Admin roll call: mark Present / Absent for each allocated student."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox, filedialog

from app.services import attendance_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, keep_selection, section_header, build_panel, build_table,
                       status_tag, style_treeview_status_tags, chip)


class AttendanceScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Attendance", "Roll call for the selected day. Students on approved leave show as Leave.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self._wrapper = wrapper
        self.tabs = tk.Frame(wrapper, bg=COLORS["background"])
        self.tabs.pack(fill="x", pady=(0, 8))
        ttk.Button(self.tabs, text="Roll call", style="Secondary.TButton",
                   command=lambda: self._show("roll")).pack(side="left", padx=(0, 8))
        self.report_tab = ttk.Button(self.tabs, text="Monthly report", style="Secondary.TButton",
                                     command=lambda: self._show("report"))
        self.report_tab.pack(side="left")
        self.roll_panel = tk.Frame(wrapper, bg=COLORS["background"])
        self.roll_panel.pack(fill="both", expand=True)
        content = build_panel(self.roll_panel, "Roll call", fonts)
        self._build_report(wrapper, fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Date", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"]).pack(side="left", padx=(0, 8))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(bar, textvariable=self.date_var, width=12).pack(side="left")
        ttk.Button(bar, text="Load", style="Secondary.TButton", command=self.refresh).pack(side="left", padx=8)
        self.summary = tk.Label(bar, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.summary.pack(side="right")
        self.tree = build_table(content, ("id", "name", "reg", "room", "status"),
                                ("ID", "Student", "Registration No.", "Room", "Status"), (45, 200, 140, 80, 90), height=12)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_att_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Attendance Record: {vals[1]}",
                    fields={
                        "Student ID": vals[0],
                        "Name": vals[1],
                        "Registration No.": vals[2],
                        "Room": vals[3],
                        "Attendance Status": vals[4],
                        "Date": self.date_var.get(),
                    },
                    full_text=f"Roll call record for {vals[1]} on {self.date_var.get()}: status is currently marked as {vals[4]}."
                )

        self.tree.bind("<Double-Button-1>", _on_att_select)
        self.tree.bind("<Return>", _on_att_select)

        self.buttons = tk.Frame(content, bg=COLORS["surface"])

        self.buttons.pack(anchor="e", pady=(10, 0))
        self.btn_present = ttk.Button(self.buttons, text="Mark Present", style="Primary.TButton",
                                      command=lambda: self.mark("Present"))
        self.btn_absent = ttk.Button(self.buttons, text="Mark Absent", style="Secondary.TButton",
                                     command=lambda: self.mark("Absent"))
        self.view_only_notice = tk.Label(self.buttons,
                                         text="View-only mode: Only Administrator & Super Admin can mark attendance.",
                                         bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=fonts["small"])

    def _build_report(self, wrapper, fonts):
        self.report_panel = tk.Frame(wrapper, bg=COLORS["background"])
        content = build_panel(self.report_panel, "Monthly attendance report", fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Month", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"]).pack(side="left", padx=(0, 8))
        self.month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(bar, textvariable=self.month_var, width=9).pack(side="left")
        ttk.Button(bar, text="Load", style="Secondary.TButton", command=self._load_report).pack(side="left", padx=8)
        ttk.Button(bar, text="Export CSV", style="Primary.TButton", command=self._export_report).pack(side="left")
        self.report_summary = tk.Label(bar, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.report_summary.pack(side="right")
        self.report_tree = build_table(content, ("name", "reg", "room", "present", "absent", "leave", "pct"),
                                       ("Student", "Registration No.", "Room", "Present", "Absent", "Leave", "Attendance %"),
                                       (180, 130, 70, 70, 70, 70, 100), height=12)
        self.report_tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.report_tree)
        self.report_tree.tag_configure("low", foreground=COLORS["danger"])

    def _show(self, which):
        if which == "report":
            self.roll_panel.pack_forget()
            self.report_panel.pack(fill="both", expand=True)
            self._load_report()
        else:
            self.report_panel.pack_forget()
            self.roll_panel.pack(fill="both", expand=True)

    def _load_report(self):
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)
        try:
            rows = attendance_service.monthly_report(self.month_var.get())
        except ValidationError as e:
            messagebox.showerror("Attendance report", str(e))
            return
        for r in rows:
            pct = "—" if r["percent"] is None else f"{r['percent']}%"
            self.report_tree.insert("", "end", values=(r["name"], r["registration_number"], r["room_number"],
                                                       r["present"], r["absent"], r["leave"], pct),
                                    tags=("low" if r["low"] else "default",))
        low = sum(1 for r in rows if r["low"])
        self.report_summary.config(text=f"Below {attendance_service.LOW_ATTENDANCE_PERCENT:.0f}%: {low}")

    def _export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile=f"attendance_{self.month_var.get()}.csv")
        if not path:
            return
        try:
            count = attendance_service.export_report_csv(self.month_var.get(), path)
            messagebox.showinfo("Export", f"Saved {count} students.")
        except ValidationError as e:
            messagebox.showerror("Attendance report", str(e))
        except Exception as e:
            handle_unexpected_error("Attendance", "export_report_ui", e)

    def mark(self, status):
        if session.get_role() not in session.ADMIN_ROLES:
            messagebox.showerror("Permission Denied", "Only Administrator and Super Admin can mark attendance.")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a student first.")
            return
        try:
            attendance_service.mark_attendance(self.tree.item(selected[0])["values"][0], self.date_var.get(), status)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Attendance", str(e))
        except Exception as e:
            handle_unexpected_error("Attendance", "mark_attendance_ui", e)

    def refresh(self):
        self.report_tab.state(["!disabled"] if session.get_role() in session.ADMIN_ROLES else ["disabled"])
        is_admin = session.get_role() in session.ADMIN_ROLES
        if is_admin:
            self.view_only_notice.pack_forget()
            self.btn_present.pack(side="left", padx=(0, 8))
            self.btn_absent.pack(side="left")
        else:
            self.btn_present.pack_forget()
            self.btn_absent.pack_forget()
            self.view_only_notice.pack(side="right")
        keep_selection(self.tree, self._rebuild)

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            roster = attendance_service.get_roster(self.date_var.get())
        except ValidationError as e:
            messagebox.showerror("Attendance", str(e))
            return
        counts = {"Present": 0, "Absent": 0, "Leave": 0, "Unmarked": 0}
        for r in roster:
            counts[r["status"]] += 1
            self.tree.insert("", "end", values=(r["student_id"], r["name"], r["registration_number"],
                                                 r["room_number"], r["status"]), tags=(status_tag(r["status"]),))
        self.summary.config(text="  ".join(f"{k}: {v}" for k, v in counts.items()))
