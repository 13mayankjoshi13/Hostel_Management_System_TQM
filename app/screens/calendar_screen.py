"""Calendar screen: month view for everyone; editors can add and delete events."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.screens.calendar_widget import CalendarWidget, KIND_COLORS
from app.services import event_service
from app.theme import COLORS, Card, section_header, form_card, form_row, button_row, build_table, split_layout
from app.utils import session
from app.utils.exception_handler import handle_unexpected_error
from app.utils.validation import ValidationError

_KINDS = ["Holiday", "Hostel Event", "Exam"]


class CalendarScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._rows = {}
        section_header(self, "Calendar", "Holidays, hostel events and exams.", fonts)

        self.left, self.right = split_layout(self)

        self.form_slot = tk.Frame(self.left, bg=COLORS["background"])
        self.form_slot.pack(fill="x")
        self._build_form()

        cal_card = Card(self.left, fit=True)
        cal_card.pack(fill="x")
        self.calendar = CalendarWidget(cal_card.body, fonts, on_select=self._on_day)
        self.calendar.pack(fill="x")
        self._cal_card = cal_card

        list_card = Card(self.right, fit=False)
        list_card.pack(fill="both", expand=True)
        tk.Label(list_card.body, text="All events", bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["section_title"]).pack(anchor="w", pady=(0, 8))
        self.tree = build_table(list_card.body, ("date", "title", "kind"),
                                  ("Date", "Title", "Type"), (110, 260, 110), height=10)
        self.tree.pack(fill="both", expand=True)
        for kind, color in KIND_COLORS.items():
            self.tree.tag_configure(f"kind_{kind}", foreground=color)
        self.delete_btn = ttk.Button(list_card.body, text="Delete Selected", style="Danger.TButton",
                                      command=self.on_delete)
        self.delete_btn.pack(anchor="e", pady=(10, 0))

    def _build_form(self):
        self.form = form_card(self.form_slot, "Add event", self.fonts)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        form_row(self.form, self.fonts, 0, "Date (YYYY-MM-DD)", ttk.Entry(self.form, textvariable=self.date_var))
        self.title_var = tk.StringVar()
        form_row(self.form, self.fonts, 1, "Title", ttk.Entry(self.form, textvariable=self.title_var))
        self.kind_var = tk.StringVar(value=_KINDS[1])
        form_row(self.form, self.fonts, 2, "Type", ttk.Combobox(
            self.form, textvariable=self.kind_var, values=_KINDS, state="readonly"))
        ttk.Button(button_row(self.form, 3), text="Add Event", style="Primary.TButton",
                    command=self.on_add).pack()

    def _is_editor(self) -> bool:
        return session.get_role() in ("Administrator", "Warden")

    def _on_day(self, day):
        self.date_var.set(day.isoformat())

    def on_add(self):
        try:
            event_service.add_event(self.date_var.get(), self.title_var.get(), self.kind_var.get())
            self.title_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Event added.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Calendar", "add_event_ui", e)

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select an event first.")
            return
        event = self._rows.get(selected[0])
        if not messagebox.askyesno("Delete Event", f"Delete '{event['title']}'?"):
            return
        try:
            event_service.delete_event(event["event_id"])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Calendar", "delete_event_ui", e)

    def refresh(self):
        if self._is_editor():
            self.form_slot.pack(fill="x", before=self._cal_card)
            self.delete_btn.pack(anchor="e", pady=(10, 0))
        else:
            self.form_slot.pack_forget()
            self.delete_btn.pack_forget()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._rows = {}
        upcoming_item = None
        for ev in event_service.get_all_events():
            item = self.tree.insert("", "end", values=(ev["event_date"], ev["title"], ev["kind"]),
                                     tags=(f"kind_{ev['kind']}",))
            self._rows[item] = ev
            if upcoming_item is None and ev["event_date"] >= date.today().isoformat():
                upcoming_item = item
        if upcoming_item:
            self.tree.see(upcoming_item)
        self.calendar.refresh()
