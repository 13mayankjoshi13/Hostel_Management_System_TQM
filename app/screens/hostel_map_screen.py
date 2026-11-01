"""Hostel map: every hostel and floor with room occupancy. Students see counts only."""
import tkinter as tk

from app.services import home_service
from app.theme import COLORS, Card, ScrollFrame, chip


class HostelMapScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        head = tk.Frame(self, bg=COLORS["background"])
        head.pack(fill="x", padx=28, pady=(8, 10))
        tk.Label(head, text="Hostel Map", bg=COLORS["background"], fg=COLORS["text_primary"],
                 font=fonts["hero"]).pack(side="left")
        legend = tk.Frame(head, bg=COLORS["background"])
        legend.pack(side="right")
        for text, fg, bg in (("Vacant", COLORS["success"], COLORS["success_soft"]),
                             ("Partly full", COLORS["warning"], COLORS["warning_soft"]),
                             ("Full", COLORS["accent"], COLORS["accent_soft"])):
            chip(legend, text, fg, bg).pack(side="left", padx=3)
        self.scroll = ScrollFrame(self, bg=COLORS["background"])
        self.scroll.pack(fill="both", expand=True, padx=28, pady=(0, 6))
        self.detail = tk.Label(self, text="Click a room to see its details.", bg=COLORS["background"],
                               fg=COLORS["text_secondary"], font=fonts["body"], anchor="w", justify="left")
        self.detail.pack(fill="x", padx=28, pady=(0, 14))

    def refresh(self):
        inner = self.scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        rooms = home_service.floor_plan()
        mine = home_service.my_room_number()
        if not rooms:
            tk.Label(inner, text="No rooms have been added yet.", bg=COLORS["background"],
                     fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(pady=20)
            return
        groups = {}
        for room in rooms:
            groups.setdefault(room["hostel_type"] or "Unassigned", {}).setdefault(room["floor"], []).append(room)
        for hostel, floors in groups.items():
            title = {"Boys": "Boys Hostel", "Girls": "Girls Hostel"}.get(hostel, "Rooms without a hostel set")
            card = Card(inner, fit=True)
            card.pack(fill="x", pady=(0, 12))
            tk.Label(card.body, text=title.upper(), bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                     font=self.fonts["small_bold"]).pack(anchor="w", pady=(0, 8))
            for floor in sorted(floors, reverse=True):
                row = tk.Frame(card.body, bg=COLORS["surface"])
                row.pack(fill="x", pady=3)
                tk.Label(row, text="Ground" if floor == 0 else f"Floor {floor}", width=8, anchor="w",
                         bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["body_bold"]).pack(side="left")
                for room in floors[floor]:
                    self._tile(row, room, room["room_number"] == mine)

    def _tile(self, parent, room, is_mine):
        taken, cap = room["taken"], room["capacity"]
        if taken == 0:
            fg, soft = COLORS["success"], COLORS["success_soft"]
        elif taken >= cap:
            fg, soft = COLORS["accent"], COLORS["accent_soft"]
        else:
            fg, soft = COLORS["warning"], COLORS["warning_soft"]
        cell = tk.Frame(parent, bg=soft, padx=10, pady=6, cursor="hand2",
                        highlightthickness=2 if is_mine else 0, highlightbackground=COLORS["text_primary"])
        cell.pack(side="left", padx=4)
        tk.Label(cell, text=room["room_number"] + (" ★" if is_mine else ""), bg=soft,
                 fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w")
        tk.Label(cell, text=f"{taken}/{cap} beds", bg=soft, fg=fg, font=self.fonts["small_bold"]).pack(anchor="w")
        for w in [cell] + list(cell.winfo_children()):
            w.bind("<Button-1>", lambda e, r=room, m=is_mine: self._show(r, m))

    def _show(self, room, is_mine):
        text = (f"Room {room['room_number']} · {room['room_type']} · floor {room['floor']} · "
                f"{room['taken']} of {room['capacity']} beds taken" + (" · your room" if is_mine else ""))
        if room["occupants"]:
            text += "\nStaying here: " + ", ".join(room["occupants"])
        self.detail.config(text=text)
