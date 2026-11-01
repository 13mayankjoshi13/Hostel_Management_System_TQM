"""Staff: send a notice to everyone, a hostel, or one student."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import notice_service, student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, form_card, build_panel, build_table, split_layout, button_row

_AUDIENCES = {"Everyone": "All", "Boys hostel": "Boys", "Girls hostel": "Girls", "One student": "Student"}


class NoticeScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._students = {}
        section_header(self, "Notices", "Send an announcement to students.", fonts)
        self.left, self.right = split_layout(self)
        form = form_card(self.left, "New notice", fonts)
        self.title_var = tk.StringVar()
        self.audience_var = tk.StringVar(value="Everyone")
        self.student_var = tk.StringVar()
        form_row(form, fonts, 0, "Title", ttk.Entry(form, textvariable=self.title_var))
        form_row(form, fonts, 1, "Send to", ttk.Combobox(form, textvariable=self.audience_var,
                                                         values=list(_AUDIENCES), state="readonly"))
        self.student_box = ttk.Combobox(form, textvariable=self.student_var, state="readonly")
        form_row(form, fonts, 2, "Student", self.student_box)
        self.body = tk.Text(form, height=6, width=30, wrap="word", relief="flat", highlightthickness=1,
                            highlightbackground=COLORS["border"], font=fonts["body"])
        form_row(form, fonts, 3, "Message", self.body)
        buttons = button_row(form, 4)
        ttk.Button(buttons, text="Send Notice", style="Primary.TButton", command=self.on_send).pack(side="left")
        content = build_panel(self.right, "Sent notices", fonts)
        self.tree = build_table(content, ("id", "title", "to", "by", "when"),
                                ("ID", "Title", "To", "By", "Sent"), (45, 210, 130, 90, 130), height=10)
        self.tree.pack(fill="both", expand=True)
        self.delete_button = ttk.Button(content, text="Delete Selected", style="Secondary.TButton",
                                        command=self.on_delete)
        self.delete_button.pack(anchor="e", pady=(10, 0))

    def on_send(self):
        try:
            audience = _AUDIENCES.get(self.audience_var.get(), "")
            sid = self._students.get(self.student_var.get())
            notice_service.send_notice(self.title_var.get(), self.body.get("1.0", "end"), audience, sid)
            self.title_var.set("")
            self.body.delete("1.0", "end")
            self.refresh()
            messagebox.showinfo("Sent", "Notice sent.")
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
        self.student_box["values"] = list(self._students)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for n in notice_service.list_notices():
            target = n["student_name"] or {"All": "Everyone", "Boys": "Boys hostel", "Girls": "Girls hostel"}[n["audience"]]
            self.tree.insert("", "end", values=(n["notice_id"], n["title"], target, n["created_by"], n["created_at"]),
                             tags=("default",))
