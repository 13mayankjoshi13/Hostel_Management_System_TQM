"""Fines screen (staff): issue fines, record cash, waive, print receipts."""
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox

from app.services import fine_service, student_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (keep_selection, COLORS, status_tag, section_header, form_row, build_panel, build_table,
                       style_treeview_status_tags, form_card, split_layout)


class FineScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._student_options = {}
        section_header(self, "Fines", "Issue fines, record cash payments and print receipts.", fonts)
        self.left, self.right = split_layout(self)

        wrapper = form_card(self.left, "Issue a fine", fonts)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(wrapper, textvariable=self.student_var, state="readonly")
        form_row(wrapper, fonts, 0, "Student", self.student_combo)
        self.amount_var = tk.StringVar()
        form_row(wrapper, fonts, 1, "Amount (₹)", ttk.Entry(wrapper, textvariable=self.amount_var))
        self.reason_var = tk.StringVar()
        form_row(wrapper, fonts, 2, "Reason", ttk.Entry(wrapper, textvariable=self.reason_var))
        ttk.Button(wrapper, text="Issue Fine", style="Primary.TButton",
                    command=self.on_issue).grid(row=3, column=1, sticky="w", pady=(10, 0))

        table_wrapper = tk.Frame(self.right, bg=COLORS["background"])
        table_wrapper.pack(fill="both", expand=True)
        content = build_panel(table_wrapper, "All Fines", fonts)
        self.tree = build_table(content, ("id", "student", "amount", "reason", "status", "method", "receipt"),
                                  ("ID", "Student", "Amount", "Reason", "Status", "Paid by", "Receipt"),
                                  (40, 140, 80, 160, 70, 70, 130), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_fine_select(event=None):
            sel = self.tree.selection()
            if not sel: return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Fine #{vals[0]} — {vals[1]}",
                    fields={
                        "Fine ID": vals[0],
                        "Student": vals[1],
                        "Amount": vals[2],
                        "Status": vals[4],
                        "Payment Method": vals[5],
                        "Receipt": vals[6],
                    },
                    full_text=f"Reason: {vals[3]}"
                )

        self.tree.bind("<Double-Button-1>", _on_fine_select)
        self.tree.bind("<Return>", _on_fine_select)

        buttons = tk.Frame(content, bg=COLORS["surface"])

        buttons.pack(anchor="e", pady=(10, 0))
        ttk.Button(buttons, text="Record Cash", style="Secondary.TButton",
                    command=lambda: self._act(fine_service.record_cash_payment, "Cash payment recorded.")).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Waive", style="Secondary.TButton",
                    command=lambda: self._act(fine_service.waive_fine, "Fine waived.")).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Check Online Payment", style="Secondary.TButton",
                    command=self.on_check).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Print Receipt", style="Primary.TButton",
                    command=self.on_print).pack(side="left")
        self.refresh()

    def _selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a fine first.")
            return None
        return self.tree.item(selected[0])["values"][0]

    def on_issue(self):
        student_id = self._student_options.get(self.student_var.get())
        try:
            fine_service.issue_fine(student_id, self.amount_var.get(), self.reason_var.get())
            self.amount_var.set("")
            self.reason_var.set("")
            self.refresh_table()
            messagebox.showinfo("Success", "Fine issued.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "issue_fine_ui", e)

    def _act(self, action, done_message):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            action(fine_id)
            self.refresh_table()
            messagebox.showinfo("Success", done_message)
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "fine_action_ui", e)

    def on_check(self):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            status = fine_service.check_online_payment(fine_id)
            self.refresh_table()
            messagebox.showinfo("Payment status", f"This fine is {status.lower()}.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "check_payment_ui", e)

    def on_print(self):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            webbrowser.open("file:///" + fine_service.print_receipt(fine_id).replace("\\", "/"))
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "print_receipt_ui", e)

    def refresh_table(self):
        keep_selection(self.tree, self._rebuild_table)

    def _rebuild_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for f in fine_service.get_all_fines():
            self.tree.insert("", "end", values=(
                f["fine_id"], f["student_name"], f["amount"], f["reason"], f["status"],
                f["payment_method"] or "—", f["receipt_number"] or "—"), tags=(status_tag(f["status"]),))

    def refresh(self):
        if session.get_role() not in session.WARDEN_ROLES:
            return
        self._student_options = {f"{s['name']} ({s['registration_number']})": s["student_id"]
                                 for s in student_service.get_all_students()}
        self.student_combo["values"] = list(self._student_options.keys())
        self.refresh_table()
