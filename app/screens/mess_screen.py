"""Mess screen: set the daily menu and read meal feedback."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import mess_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_panel, build_table, section_header, form_card, form_row, split_layout, style_treeview_status_tags


class MessScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Mess", "Set the daily menu and see what students think of it.", fonts)
        self.left, self.right = split_layout(self, 440)
        self.card = form_card(self.left, "Daily menu", fonts)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        date_row = ttk.Entry(self.card, textvariable=self.date_var)
        form_row(self.card, fonts, 0, "Date (YYYY-MM-DD)", date_row)
        ttk.Button(self.card, text="Load day", style="Secondary.TButton", command=self.load_day).grid(
            row=1, column=1, sticky="w", pady=(0, 6))
        self.vars = {}
        for i, meal in enumerate(mess_service.MEALS):
            self.vars[meal] = tk.StringVar()
            form_row(self.card, fonts, 2 + i, meal, ttk.Entry(self.card, textvariable=self.vars[meal]))
        self.save_button = ttk.Button(self.card, text="Save Menu", style="Primary.TButton", command=self.save)
        self.save_button.grid(row=7, column=1, sticky="w", pady=(10, 0))
        content = build_panel(self.right, "Student feedback, last 7 days", fonts)
        self.tree = build_table(content, ("meal", "votes", "avg", "flag"), ("Meal", "Ratings", "Average (of 5)", "Note"),
                                (110, 80, 110, 140), height=4)
        self.tree.pack(fill="x")
        style_treeview_status_tags(self.tree)
        self.tree.tag_configure("low", foreground=COLORS["danger"])
        tk.Label(content, text="Recent comments", bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                 font=fonts["small_bold"]).pack(anchor="w", pady=(14, 4))
        self.comments = build_table(content, ("date", "meal", "rating", "comment"), ("Date", "Meal", "Rating", "Comment"),
                                    (90, 80, 60, 260), height=6)
        self.comments.pack(fill="both", expand=True)
        style_treeview_status_tags(self.comments)

    def load_day(self):
        try:
            menu = mess_service.get_menu(self.date_var.get())
        except ValidationError as e:
            messagebox.showerror("Mess", str(e))
            return
        for meal, items in menu.items():
            self.vars[meal].set(items)

    def save(self):
        saved = 0
        try:
            for meal, var in self.vars.items():
                if var.get().strip():
                    mess_service.set_menu(self.date_var.get(), meal, var.get())
                    saved += 1
            if not saved:
                raise ValidationError("Write at least one meal's menu.")
            messagebox.showinfo("Mess", f"Saved {saved} meal(s).")
        except ValidationError as e:
            messagebox.showerror("Mess", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "set_menu_ui", e)

    def refresh(self):
        role = session.get_role()
        if role not in session.MESS_VIEW_ROLES:
            return
        can_edit = role in session.MESS_MANAGE_ROLES
        self.save_button.state(["!disabled"] if can_edit else ["disabled"])
        self.load_day()
        for tree in (self.tree, self.comments):
            for row in tree.get_children():
                tree.delete(row)
        for r in mess_service.feedback_summary():
            avg = "-" if r["average"] is None else f"{r['average']:.1f}"
            self.tree.insert("", "end", values=(r["meal"], r["votes"], avg, "Needs attention" if r["low"] else ""),
                             tags=("low" if r["low"] else "default",))
        for c in mess_service.recent_comments():
            self.comments.insert("", "end", values=(c["menu_date"], c["meal"], c["rating"], c["comment"]), tags=("default",))
