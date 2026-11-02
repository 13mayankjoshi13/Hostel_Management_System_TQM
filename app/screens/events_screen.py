"""Events: upcoming hostel events, holidays and exams, with a filter. Editors add events here."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from app.services import event_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, build_panel, build_table, form_card, form_row, split_layout, button_row

_KINDS = ("All", "Hostel Event", "Holiday", "Exam")


class EventsScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Hostel Events", "What is coming up in the hostel and the university.", fonts)
        self.left, self.right = split_layout(self)
        self.form_host = tk.Frame(self.left, bg=COLORS["background"])
        self.form_host.pack(fill="x")
        form = form_card(self.form_host, "Add an event", fonts)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.title_var = tk.StringVar()
        self.kind_var = tk.StringVar(value="Hostel Event")
        form_row(form, fonts, 0, "Date (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.date_var))
        form_row(form, fonts, 1, "Title", ttk.Entry(form, textvariable=self.title_var))
        form_row(form, fonts, 2, "Type", ttk.Combobox(form, textvariable=self.kind_var,
                                                       values=_KINDS[1:], state="readonly"))
        buttons = button_row(form, 3)
        ttk.Button(buttons, text="Add Event", style="Primary.TButton", command=self.on_add).pack(side="left")
        ttk.Button(buttons, text="Delete Selected", style="Secondary.TButton",
                   command=self.on_delete).pack(side="left", padx=(8, 0))
        content = build_panel(self.right, "Upcoming", fonts)
        bar = tk.Frame(content, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Show", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 font=fonts["label"]).pack(side="left", padx=(0, 8))
        self.filter_var = tk.StringVar(value="All")
        box = ttk.Combobox(bar, textvariable=self.filter_var, values=_KINDS, state="readonly", width=14)
        box.pack(side="left")
        box.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.tree = build_table(content, ("id", "date", "title", "kind"), ("ID", "Date", "Title", "Type"),
                                (40, 100, 260, 110), height=12)
        self.tree.pack(fill="both", expand=True)

        def _on_event_select(event=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0], "values")
            if vals:
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    title=f"Event: {vals[2]}",
                    fields={
                        "Event ID": vals[0],
                        "Date": vals[1],
                        "Title": vals[2],
                        "Type": vals[3],
                    },
                    full_text=f"The '{vals[2]}' event is scheduled on {vals[1]} ({vals[3]})."
                )

        self.tree.bind("<Double-Button-1>", _on_event_select)
        self.tree.bind("<Return>", _on_event_select)


    def _can_edit(self):
        return session.get_role() in session.WARDEN_ROLES

    def on_add(self):
        try:
            event_service.add_event(self.date_var.get(), self.title_var.get(), self.kind_var.get())
            self.title_var.set("")
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Calendar", "add_event_ui", e)

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select an event first.")
            return
        try:
            event_service.delete_event(self.tree.item(selected[0])["values"][0])
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Event", str(e))
        except Exception as e:
            handle_unexpected_error("Calendar", "delete_event_ui", e)

    def refresh(self):
        if self._can_edit():
            self.form_host.pack(fill="x")
        else:
            self.form_host.pack_forget()
        for row in self.tree.get_children():
            self.tree.delete(row)
        wanted = self.filter_var.get()
        for e in event_service.get_upcoming(date.today().isoformat(), 500):
            if wanted == "All" or e["kind"] == wanted:
                self.tree.insert("", "end", values=(e["event_id"], e["event_date"], e["title"], e["kind"]),
                                 tags=("default",))
