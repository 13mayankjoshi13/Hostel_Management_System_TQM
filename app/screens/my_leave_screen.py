"""Student portal: apply for leave and mark yourself returned."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import student_portal_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, status_tag, section_header, form_row, build_panel, build_table, style_treeview_status_tags, form_card, split_layout


class MyLeaveScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Leave", "Let the hostel know when you are away.", fonts)
        self.left, self.right = split_layout(self)

        wrapper = form_card(self.left, "Apply for leave", self.fonts)
        self.from_var = tk.StringVar(value=date.today().isoformat())
        form_row(wrapper, fonts, 0, "From (YYYY-MM-DD)", ttk.Entry(wrapper, textvariable=self.from_var))
        self.to_var = tk.StringVar(value=date.today().isoformat())
        form_row(wrapper, fonts, 1, "To (YYYY-MM-DD)", ttk.Entry(wrapper, textvariable=self.to_var))
        self.reason_var = tk.StringVar()
        form_row(wrapper, fonts, 2, "Reason", ttk.Entry(wrapper, textvariable=self.reason_var))
        ttk.Button(wrapper, text="Apply for Leave", style="Primary.TButton",
                    command=self.on_apply).grid(row=3, column=1, sticky="w", pady=(10, 0))

        table_wrapper = tk.Frame(self.right, bg=COLORS["background"])
        table_wrapper.pack(fill="both", expand=True)
        content = build_panel(table_wrapper, "My Leaves", fonts)
        self.tree = build_table(content, ("id", "room", "from", "to", "reason", "status"),
                                  ("ID", "Room", "From", "To", "Reason", "Status"),
                                  (45, 70, 100, 100, 220, 90), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        def _on_leave_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Leave Application #{vals[0]}",
                    fields={
                        "Leave ID": vals[0],
                        "Room": vals[1],
                        "From Date": vals[2],
                        "To Date": vals[3],
                        "Status": vals[5],
                    },
                    full_text=f"Reason: {vals[4]}"
                )

        self.tree.bind("<Double-Button-1>", _on_leave_select)
        self.tree.bind("<Return>", _on_leave_select)

        info_strip = tk.Frame(content, bg=COLORS["surface"], pady=4)
        info_strip.pack(fill="x", pady=(10, 0))
        tk.Label(info_strip, text="ℹ Note: Return from leave must be verified & marked by Warden / Admin upon hostel check-in.",
                 bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(anchor="w")


    def on_apply(self):
        try:
            student_portal_service.apply_leave(self.from_var.get(), self.to_var.get(), self.reason_var.get())
            self.reason_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Leave recorded.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Portal", "apply_leave_ui", e)

    def on_return(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a leave first.")
            return
        try:
            student_portal_service.return_from_leave(self.tree.item(selected[0])["values"][0])
            self.refresh()
            messagebox.showinfo("Success", "Marked as returned.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Portal", "return_from_leave_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for l in student_portal_service.my_leaves():
            self.tree.insert("", "end", values=(
                l["leave_id"], l["room_number"], l["from_date"], l["to_date"], l["reason"], l["status"]),
                tags=(status_tag(l["status"]),))
