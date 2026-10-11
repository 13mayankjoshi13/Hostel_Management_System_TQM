"""Student portal: file a complaint and follow its status."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_portal_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (COLORS, section_header, form_row, build_panel, build_table,
                        style_treeview_status_tags, status_tag)

_CATEGORIES = ["Maintenance", "Washroom", "Cleanliness", "Noise", "Security", "Food", "Other"]


class MyComplaintsScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Complaints", "Report a problem and follow its progress.", fonts)

        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)
        self.category_var = tk.StringVar(value=_CATEGORIES[0])
        form_row(wrapper, fonts, 0, "Category", ttk.Combobox(
            wrapper, textvariable=self.category_var, values=_CATEGORIES, state="readonly"))
        self.description_text = tk.Text(wrapper, height=3, wrap="word", font=fonts["body"],
                                          relief="solid", bd=1, bg=COLORS["surface"],
                                          fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                                          highlightbackground=COLORS["border_strong"],
                                          highlightcolor=COLORS["accent"])
        form_row(wrapper, fonts, 1, "Description", self.description_text)
        ttk.Button(wrapper, text="Submit Complaint", style="Primary.TButton",
                    command=self.on_submit).grid(row=2, column=1, sticky="w", pady=(10, 0))

        table_wrapper = tk.Frame(self, bg=COLORS["background"])
        table_wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(table_wrapper, "My Complaints", fonts)
        self.tree = build_table(content, ("id", "category", "description", "status", "assigned", "date"),
                                  ("ID", "Category", "Description", "Status", "Handled by", "Filed"),
                                  (45, 100, 280, 90, 120, 140), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

    def on_submit(self):
        try:
            student_portal_service.file_complaint(
                self.category_var.get(), self.description_text.get("1.0", "end").strip())
            self.description_text.delete("1.0", "end")
            self.refresh()
            messagebox.showinfo("Success", "Your complaint has been submitted.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Portal", "file_complaint_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in student_portal_service.my_complaints():
            self.tree.insert("", "end", values=(
                c["complaint_id"], c["category"], c["description"], c["status"],
                c["assigned_to"] or "—", c["created_at"]), tags=(status_tag(c["status"]),))
