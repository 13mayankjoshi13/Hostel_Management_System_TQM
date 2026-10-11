"""Student portal: the student's own room."""
import tkinter as tk

from app.services import student_portal_service
from app.theme import COLORS, section_header, build_panel


class MyRoomScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Room", "Your current room allotment.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 0))
        self.panel = build_panel(wrapper, "Allotment", fonts)
        self.rows = {}
        for key, label in (("room_number", "Room"), ("room_type", "Type"),
                            ("capacity", "Capacity"), ("allocated_at", "Allotted on")):
            row = tk.Frame(self.panel, bg=COLORS["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=14, anchor="w", bg=COLORS["surface"],
                      fg=COLORS["text_secondary"], font=fonts["label"]).pack(side="left")
            value = tk.Label(row, text="", anchor="w", bg=COLORS["surface"],
                              fg=COLORS["text_primary"], font=fonts["body"])
            value.pack(side="left")
            self.rows[key] = value
        self.message = tk.Label(self.panel, text="", anchor="w", bg=COLORS["surface"],
                                 fg=COLORS["text_secondary"], font=fonts["body"])
        self.message.pack(fill="x", pady=(6, 0))

    def refresh(self):
        room = student_portal_service.my_room()
        for key, label in self.rows.items():
            label.configure(text=str(room[key]) if room else "—")
        self.message.configure(text="" if room else "No room has been allotted to you yet.")
