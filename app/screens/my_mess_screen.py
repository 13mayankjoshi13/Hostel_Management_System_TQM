"""Student view of today's menu, with a 1 to 5 rating per meal."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import mess_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, Card, section_header


class MyMessScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Mess", "Today's menu. Join the queue, then rate each meal after you eat it.", fonts)
        self.body = tk.Frame(self, bg=COLORS["background"])
        self.body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

    def refresh(self):
        for w in self.body.winfo_children():
            w.destroy()
        today = date.today().isoformat()
        menu = mess_service.get_menu(today)
        mine = mess_service.my_ratings(today)
        queue = mess_service.my_queue_status(today)
        waiting = mess_service.queue_counts(today)
        for meal, items in menu.items():
            card = Card(self.body, fit=True)
            card.pack(fill="x", pady=(0, 10))
            top = tk.Frame(card.body, bg=COLORS["surface"])
            top.pack(fill="x")
            tk.Label(top, text=meal, bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["section_title"]).pack(side="left")
            tk.Label(card.body, text=items or "No menu set yet.", bg=COLORS["surface"],
                     fg=COLORS["text_secondary"] if items else COLORS["text_tertiary"], font=self.fonts["body"],
                     wraplength=760, justify="left").pack(anchor="w", pady=(4, 6))
            if not items:
                continue
            q = queue.get(meal)
            qrow = tk.Frame(card.body, bg=COLORS["surface"])
            qrow.pack(fill="x", pady=(0, 6))
            if q is None:
                text = f"{waiting[meal]} waiting"
            elif q["status"] == "Served":
                text = "Served"
            else:
                text = f"You are #{q['position']} in the queue ({waiting[meal]} waiting)"
            tk.Label(qrow, text=text, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["label"]).pack(side="left", padx=(0, 12))
            if q is None:
                ttk.Button(qrow, text="Join queue", style="Secondary.TButton",
                           command=lambda m=meal: self._queue(mess_service.join_queue, m)).pack(side="left")
            elif q["status"] == "Waiting":
                ttk.Button(qrow, text="Leave queue", style="Secondary.TButton",
                           command=lambda m=meal: self._queue(mess_service.leave_queue, m)).pack(side="left")
            row = tk.Frame(card.body, bg=COLORS["surface"])
            row.pack(fill="x")
            rating = tk.StringVar(value=str(mine.get(meal, 5)))
            comment = tk.StringVar()
            tk.Label(row, text="Rating", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["label"]).pack(side="left")
            ttk.Combobox(row, textvariable=rating, values=["1", "2", "3", "4", "5"], state="readonly", width=3).pack(side="left", padx=(6, 12))
            ttk.Entry(row, textvariable=comment, width=36).pack(side="left", padx=(0, 10))
            ttk.Button(row, text="Update rating" if meal in mine else "Submit rating", style="Primary.TButton",
                       command=lambda m=meal, r=rating, c=comment: self._submit(m, r, c)).pack(side="left")

    def _submit(self, meal, rating, comment):
        try:
            mess_service.submit_feedback(date.today().isoformat(), meal, rating.get(), comment.get())
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Mess", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "submit_feedback_ui", e)

    def _queue(self, action, meal):
        try:
            action(meal)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Mess", str(e))
        except Exception as e:
            handle_unexpected_error("Mess", "mess_queue_ui", e)
