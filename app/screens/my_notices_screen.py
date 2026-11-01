"""Student portal: notices addressed to you, your hostel, or everyone."""
import tkinter as tk

from app.services import notice_service
from app.theme import COLORS, section_header, build_panel


class MyNoticesScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Notices", "Announcements from the hostel office.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.content = build_panel(wrapper, "Latest", fonts)

    def refresh(self):
        for child in self.content.winfo_children():
            child.destroy()
        notices = notice_service.notices_for_student()
        if not notices:
            tk.Label(self.content, text="No notices yet.", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["body"]).pack(anchor="w")
        for n in notices:
            tk.Label(self.content, text=n["title"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=self.fonts["heading"] if "heading" in self.fonts else self.fonts["body"]).pack(anchor="w", pady=(8, 0))
            tk.Label(self.content, text=f"{n['created_by']} · {n['created_at']}", bg=COLORS["surface"],
                     fg=COLORS["text_tertiary"], font=self.fonts["label"]).pack(anchor="w")
            tk.Label(self.content, text=n["body"], bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["body"], wraplength=640, justify="left").pack(anchor="w", pady=(2, 4))
