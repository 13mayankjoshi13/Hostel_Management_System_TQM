"""Hostel map: every hostel and floor with room occupancy. Students see counts only."""
import tkinter as tk

from app.services import home_service
from app.theme import COLORS, Card, ScrollFrame, chip, section_header


_TITLES = {"Boys": "Boys Hostel", "Girls": "Girls Hostel"}
_FLOOR_H = 92
_MAX_DOTS = 10


def _status(room):
    taken, cap = room["taken"], room["capacity"]
    if taken == 0:
        return COLORS["success"], COLORS["success_soft"], "Vacant"
    if taken >= cap:
        return COLORS["accent"], COLORS["accent_soft"], "Full"
    return COLORS["warning"], COLORS["warning_soft"], "Partly full"


class HostelMapScreen(tk.Frame):
    """Each hostel is a building card; floors stack top to bottom and the room tiles share the width."""

    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Hostel Map", "Every hostel by floor. Click a room for details, double-click for more.", fonts)
        legend = tk.Frame(self, bg=COLORS["background"])
        legend.pack(fill="x", padx=28, pady=(0, 8))
        for text, fg, bg in (("Vacant", COLORS["success"], COLORS["success_soft"]),
                             ("Partly full", COLORS["warning"], COLORS["warning_soft"]),
                             ("Full", COLORS["accent"], COLORS["accent_soft"])):
            chip(legend, text, fg, bg).pack(side="left", padx=(0, 6))
        self.scroll = ScrollFrame(self, bg=COLORS["background"])
        self.scroll.pack(fill="both", expand=True, padx=28, pady=(0, 6))
        self.scroll.canvas.bind("<Configure>", self._fit_height)
        self.detail = tk.Label(self, text="Click a room to see its details.", bg=COLORS["background"],
                               fg=COLORS["text_secondary"], font=fonts["body"], anchor="w", justify="left")
        self.detail.pack(fill="x", padx=28, pady=(0, 14))

    def _schedule_fit(self):
        job = getattr(self, "_fit_job", None)
        if job:
            self.after_cancel(job)
        self._fit_job = self.after(10, self._fit_height)

    def destroy(self):
        job = getattr(self, "_fit_job", None)
        if job:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        super().destroy()

    def _fit_height(self, event=None):
        self._fit_job = None
        """Stretch the map to the visible area when it is shorter; scroll when it is taller."""
        canvas = self.scroll.canvas
        canvas.itemconfigure(self.scroll._win, width=canvas.winfo_width(),
                             height=max(canvas.winfo_height(), self.scroll.inner.winfo_reqheight()))

    def refresh(self):
        inner = self.scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        rooms = home_service.floor_plan()
        mine = home_service.my_room_number()
        if not rooms:
            tk.Label(inner, text="No rooms have been added yet.", bg=COLORS["background"],
                     fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(pady=20)
            self._schedule_fit()
            return
        groups = {}
        for room in rooms:
            groups.setdefault(room["hostel_type"] or "Unassigned", {}).setdefault(room["floor"], []).append(room)
        inner.rowconfigure(0, weight=1)
        for col, (hostel, floors) in enumerate(groups.items()):
            inner.columnconfigure(col, weight=1, uniform="building")
            self._building(inner, col, len(groups), hostel, floors, mine)
        self._schedule_fit()

    def _building(self, parent, col, count, hostel, floors, mine):
        members = [r for rooms in floors.values() for r in rooms]
        beds, taken = sum(r["capacity"] for r in members), sum(r["taken"] for r in members)
        percent = round(taken / beds * 100) if beds else 0
        card = Card(parent, fit=False)
        card.configure(height=110 + len(floors) * _FLOOR_H)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0 if col == count - 1 else 8), pady=(0, 8))
        body = card.body
        top = tk.Frame(body, bg=COLORS["surface"])
        top.pack(fill="x")
        tk.Label(top, text=_TITLES.get(hostel, "Rooms without a hostel set"), bg=COLORS["surface"],
                 fg=COLORS["text_primary"], font=self.fonts["section_title"]).pack(side="left")
        tk.Label(top, text=f"{taken} of {beds} beds · {percent}%", bg=COLORS["surface"],
                 fg=COLORS["text_secondary"], font=self.fonts["label"]).pack(side="right")
        bar = tk.Canvas(body, height=8, bg=COLORS["surface"], highlightthickness=0)
        bar.pack(fill="x", pady=(6, 10))
        bar.bind("<Configure>", lambda e, b=bar, p=percent: self._draw_bar(b, p))
        stack = tk.Frame(body, bg=COLORS["surface"])
        stack.pack(fill="both", expand=True)
        for row, floor in enumerate(sorted(floors, reverse=True)):
            stack.rowconfigure(row, weight=1, uniform="floor")
            line = tk.Frame(stack, bg=COLORS["surface"])
            line.grid(row=row, column=0, sticky="nsew", pady=3)
            line.rowconfigure(0, weight=1)
            tk.Label(line, text="Ground" if floor == 0 else f"Floor {floor}", width=7, anchor="w",
                     bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=self.fonts["small_bold"]).grid(
                row=0, column=0, sticky="w")
            for i, room in enumerate(sorted(floors[floor], key=lambda r: r["room_number"])):
                line.columnconfigure(i + 1, weight=1, uniform="room")
                self._tile(line, i + 1, room, room["room_number"] == mine)
        stack.columnconfigure(0, weight=1)

    def _draw_bar(self, bar, percent):
        bar.delete("all")
        w = max(bar.winfo_width(), 10)
        bar.create_rectangle(0, 0, w, 8, fill=COLORS["border"], outline="")
        if percent:
            bar.create_rectangle(0, 0, w * min(percent, 100) / 100, 8, fill=COLORS["accent"], outline="")

    def _tile(self, parent, column, room, is_mine):
        taken, cap = room["taken"], room["capacity"]
        fg, soft, label = _status(room)
        cell = tk.Frame(parent, bg=soft, padx=10, pady=8, cursor="hand2",
                        highlightthickness=2 if is_mine else 1,
                        highlightbackground=COLORS["text_primary"] if is_mine else COLORS["border"])
        cell.grid(row=0, column=column, sticky="nsew", padx=4)
        tk.Label(cell, text=room["room_number"] + (" \u2605" if is_mine else ""), bg=soft,
                 fg=COLORS["text_primary"], font=self.fonts["body_bold"]).pack(anchor="w")
        tk.Label(cell, text=label, bg=soft, fg=fg, font=self.fonts["small_bold"]).pack(anchor="w")
        tk.Label(cell, text=room["room_type"], bg=soft, fg=COLORS["text_secondary"],
                 font=self.fonts["small"]).pack(anchor="w")
        if cap <= _MAX_DOTS:
            dots = tk.Canvas(cell, width=cap * 16, height=14, bg=soft, highlightthickness=0)
            for i in range(cap):
                dots.create_oval(2 + i * 16, 2, 12 + i * 16, 12, fill=fg if i < taken else soft, outline=fg, width=2)
            dots.pack(anchor="w", pady=(6, 0))
        else:
            tk.Label(cell, text=f"{taken}/{cap} beds", bg=soft, fg=fg, font=self.fonts["small_bold"]).pack(anchor="w")

        def bind_all(widget):
            widget.bind("<Button-1>", lambda e, r=room, m=is_mine: self._show(r, m))
            widget.bind("<Double-Button-1>", lambda e, r=room, m=is_mine: self._show_modal(r, m))
            for child in widget.winfo_children():
                bind_all(child)

        bind_all(cell)

    def _show(self, room, is_mine):
        text = (f"Room {room['room_number']} · {room['room_type']} · floor {room['floor']} · "
                f"{room['taken']} of {room['capacity']} beds taken" + (" · your room" if is_mine else ""))
        if room["occupants"]:
            text += "\nStaying here: " + ", ".join(room["occupants"])
        self.detail.config(text=text)

    def _show_modal(self, room, is_mine):
        from app.theme import show_detail_dialog
        occupants_text = ", ".join(room["occupants"]) if room["occupants"] else "No occupants currently allocated."
        show_detail_dialog(
            title=f"Room {room['room_number']} Details" + (" (Your Room)" if is_mine else ""),
            fields={
                "Room Number": room["room_number"],
                "Hostel": room.get("hostel_type") or "Unassigned",
                "Floor": "Ground" if room["floor"] == 0 else f"Floor {room['floor']}",
                "Type": room["room_type"],
                "Occupancy": f"{room['taken']} / {room['capacity']} beds taken",
            },
            full_text=f"Current Occupants:\n{occupants_text}"
        )

