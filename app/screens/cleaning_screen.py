"""Cleaning checklist: every hostel floor, four areas, reset each day."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import housekeeping_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_panel, build_table, keep_selection, section_header, style_treeview_status_tags


class CleaningScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Cleaning", "Tick off each area as it is cleaned. The list starts fresh every day.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        content = build_panel(wrapper, "Today's checklist", fonts)
        self.progress = tk.Label(content, text="", bg=COLORS["surface"], fg=COLORS["text_secondary"], font=fonts["label"])
        self.progress.pack(anchor="e")
        cols = ("hostel", "floor") + tuple(a.lower().replace(" ", "_") for a in housekeeping_service.AREAS) + ("done",)
        heads = ("Hostel", "Floor") + housekeeping_service.AREAS + ("Done",)
        self.tree = build_table(content, cols, heads, (90, 60, 90, 90, 100, 80, 70), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.buttons = tk.Frame(content, bg=COLORS["surface"])
        self.buttons.pack(anchor="e", pady=(10, 0))
        self.area_var = tk.StringVar(value=housekeeping_service.AREAS[0])
        ttk.Combobox(self.buttons, textvariable=self.area_var, values=housekeeping_service.AREAS, state="readonly",
                     width=14).pack(side="left", padx=(0, 8))
        self.done_button = ttk.Button(self.buttons, text="Mark Cleaned", style="Primary.TButton", command=lambda: self.mark(True))
        self.undo_button = ttk.Button(self.buttons, text="Undo", style="Secondary.TButton", command=lambda: self.mark(False))
        self.done_button.pack(side="left", padx=(0, 8))
        self.undo_button.pack(side="left")

    def mark(self, done):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("No Selection", "Select a floor first.")
            return
        vals = self.tree.item(sel[0])["values"]
        try:
            housekeeping_service.set_done(vals[0], vals[1], self.area_var.get(), done)
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Cleaning", str(e))
        except Exception as e:
            handle_unexpected_error("Cleaning", "set_done_ui", e)

    def refresh(self):
        role = session.get_role()
        if role not in session.CLEANING_VIEW_ROLES:
            return
        for b in (self.done_button, self.undo_button):
            b.state(["!disabled"] if role in session.CLEANING_MANAGE_ROLES else ["disabled"])
        keep_selection(self.tree, self._rebuild)
        p = housekeeping_service.progress()
        self.progress.config(text=f"{p['done']} of {p['total']} areas cleaned ({p['percent']}%)")

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in housekeeping_service.checklist():
            marks = tuple("✓" if r["areas"][a] else "-" for a in housekeeping_service.AREAS)
            self.tree.insert("", "end", values=(r["hostel"], r["floor"]) + marks + (f"{r['done']}/{r['total']}",),
                             tags=("status_resolved" if r["done"] == r["total"] else "default",))
