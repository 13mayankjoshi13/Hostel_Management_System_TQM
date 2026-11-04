"""Shift log: specialists record issues and follow-ups; wardens and admins read them."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import staff_log_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_panel, build_table, section_header


class StaffLogScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        section_header(self, "Shift Log", "Record issues and follow-ups from your shift.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.panel = build_panel(wrapper, "Entries", fonts)
        self.form = tk.Frame(self.panel, bg=COLORS["surface"])
        self.kind = tk.StringVar()
        self.details = tk.StringVar()
        self.combo = ttk.Combobox(self.form, textvariable=self.kind, state="readonly", width=20)
        self.combo.pack(side="left", padx=(0, 8))
        entry = ttk.Entry(self.form, textvariable=self.details, width=52)
        entry.pack(side="left", padx=(0, 8))
        entry.bind("<Return>", lambda _e: self.on_add())
        ttk.Button(self.form, text="Add", style="Primary.TButton", command=self.on_add).pack(side="left")
        self.tree = build_table(self.panel, ("id", "role", "kind", "details", "status", "by", "at"),
                                ("ID", "Role", "Type", "Details", "Status", "By", "Time"),
                                (45, 120, 120, 300, 70, 100, 130), height=12)
        self.tree.pack(fill="both", expand=True)
        self.done_btn = ttk.Button(self.panel, text="Mark Done", style="Secondary.TButton", command=self.on_done)

    def on_add(self):
        try:
            staff_log_service.add_entry(self.kind.get(), self.details.get())
            self.details.set("")
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Shift Log", str(e))
        except Exception as e:
            handle_unexpected_error("ShiftLog", "add_entry_ui", e)

    def on_done(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("No Selection", "Select an entry first.")
            return
        try:
            staff_log_service.mark_done(self.tree.item(sel[0])["values"][0])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Shift Log", str(e))
        except Exception as e:
            handle_unexpected_error("ShiftLog", "mark_done_ui", e)

    def refresh(self):
        writer = session.get_role() in staff_log_service.KINDS
        self.form.pack_forget()
        self.done_btn.pack_forget()
        if writer:
            kinds = staff_log_service.kinds_for_role()
            self.combo["values"] = kinds
            if self.kind.get() not in kinds:
                self.kind.set(kinds[0])
            self.form.pack(fill="x", pady=(0, 10), before=self.tree)
            self.done_btn.pack(anchor="e", pady=(10, 0))
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in staff_log_service.list_entries():
            self.tree.insert("", "end", values=(r["log_id"], r["role"], r["kind"], r["details"], r["status"],
                                                r["created_by"], r["created_at"]), tags=("default",))
