"""Student portal: see your fines, pay online with Razorpay, print receipts."""
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox

from app.services import fine_service, student_portal_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (keep_selection, COLORS, status_tag, section_header, build_panel, build_table,
                       style_treeview_status_tags)


class MyFinesScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Fines", "Pay a fine online, then print your receipt.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        content = build_panel(wrapper, "Fines", fonts)
        self.tree = build_table(content, ("id", "amount", "reason", "status", "paid", "receipt"),
                                  ("ID", "Amount", "Reason", "Status", "Paid on", "Receipt"),
                                  (45, 90, 260, 80, 140, 140), height=8)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_fine_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Fine Record #{vals[0]}",
                    fields={
                        "Fine ID": vals[0],
                        "Amount": vals[1],
                        "Status": vals[3],
                        "Paid On": vals[4],
                        "Receipt": vals[5],
                    },
                    full_text=f"Reason: {vals[2]}"
                )

        self.tree.bind("<Double-Button-1>", _on_fine_select)
        self.tree.bind("<Return>", _on_fine_select)

        buttons = tk.Frame(content, bg=COLORS["surface"])

        buttons.pack(anchor="e", pady=(10, 0))
        ttk.Button(buttons, text="Pay Online", style="Primary.TButton",
                    command=self.on_pay).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="I Have Paid — Check", style="Secondary.TButton",
                    command=self.on_check).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Print Receipt", style="Secondary.TButton",
                    command=self.on_print).pack(side="left")

    def _selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a fine first.")
            return None
        return self.tree.item(selected[0])["values"][0]

    def on_pay(self):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            fine_service.open_payment_page(fine_service.start_online_payment(fine_id))
            messagebox.showinfo("Complete the payment",
                                "The payment page opened in your browser. After paying, come back and "
                                "click 'I Have Paid — Check'.")
        except ValidationError as e:
            messagebox.showerror("Payment", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "pay_online_ui", e)

    def on_check(self):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            status = fine_service.check_online_payment(fine_id)
            self.refresh()
            if status == "Paid":
                messagebox.showinfo("Payment received", "Payment confirmed. You can print your receipt now.")
            else:
                messagebox.showinfo("Payment status", f"This fine is {status.lower()}. If you just paid, wait a few seconds and check again.")
        except ValidationError as e:
            messagebox.showerror("Payment", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "check_payment_ui", e)

    def on_print(self):
        fine_id = self._selected_id()
        if fine_id is None:
            return
        try:
            webbrowser.open("file:///" + fine_service.print_receipt(fine_id).replace("\\", "/"))
        except ValidationError as e:
            messagebox.showerror("Receipt", str(e))
        except Exception as e:
            handle_unexpected_error("Fine", "print_receipt_ui", e)

    def refresh(self):
        keep_selection(self.tree, self._rebuild)

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for f in student_portal_service.my_fines():
            self.tree.insert("", "end", values=(
                f["fine_id"], f["amount"], f["reason"], f["status"], f["paid_at"] or "—",
                f["receipt_number"] or "—"), tags=(status_tag(f["status"]),))
