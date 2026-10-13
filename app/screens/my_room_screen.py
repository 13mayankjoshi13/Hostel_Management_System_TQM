"""Student portal: the student's own room."""
import tkinter as tk

from app.services import student_portal_service
from app.screens.calendar_widget import UpcomingList
from app.theme import COLORS, Card, section_header


class MyRoomScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Room", "Your current room allotment.", fonts)
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 0))
        card = Card(wrapper, fit=True)
        card.pack(fill="x")
        tk.Label(card.body, text="Allotment", bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["section_title"]).pack(anchor="w", pady=(0, 8))
        self.panel = card.body
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
        up = Card(wrapper, fit=True)
        up.pack(fill="x", pady=(16, 0))
        tk.Label(up.body, text="Upcoming holidays and events", bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["section_title"]).pack(anchor="w", pady=(0, 8))
        self.upcoming = UpcomingList(up.body, fonts, limit=5)
        self.upcoming.pack(fill="x")
        self.message = tk.Label(self.panel, text="", anchor="w", bg=COLORS["surface"],
                                 fg=COLORS["text_secondary"], font=fonts["body"])
        self.message.pack(fill="x", pady=(6, 0))

    def refresh(self):
        room = student_portal_service.my_room()
        for key, label in self.rows.items():
            label.configure(text=str(room[key]) if room else "—")
        self.message.configure(text="" if room else "No room has been allotted to you yet.")
        self.upcoming.refresh()
