"""Hostel map: every hostel and floor with room occupancy. Students see counts only."""
import tkinter as tk
from tkinter import ttk

from app.services import home_service
from app.theme import COLORS, Card, ScrollFrame, chip, section_header


_TITLES = {"Boys": "Boys Hostel", "Girls": "Girls Hostel"}
_COLUMNS = 6
_MAX_DOTS = 10
_FLOOR_FACILITIES = ("Washroom", "Washroom", "Water cooler", "Stairs")
_GROUND_FACILITIES = ("Entrance", "Warden office", "Common room", "Mess", "Washroom", "Water cooler")
_FACILITY_COLORS = {"Washroom": "info", "Water cooler": "teal", "Stairs": "text_tertiary", "Entrance": "accent",
                    "Warden office": "orange", "Common room": "pink", "Mess": "success"}
_ALL = "All"
_SORTS = {"Room number": lambda r: r["room_number"],
          "Most vacant first": lambda r: (-(r["capacity"] - r["taken"]), r["room_number"]),
          "Most occupied first": lambda r: (-r["taken"], r["room_number"])}


def _floor_name(floor):
    return "Ground floor" if floor == 0 else f"Floor {floor}"


def _status(room):
    taken, cap = room["taken"], room["capacity"]
    if taken == 0:
        return COLORS["success"], COLORS["success_soft"], "Vacant"
    if taken >= cap:
        return COLORS["accent"], COLORS["accent_soft"], "Full"
    return COLORS["warning"], COLORS["warning_soft"], "Partly full"


class HostelMapScreen(tk.Frame):
    """Hostels stacked top to bottom; each floor is a block with its facilities and wrapped room tiles."""

    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._rooms = []
        section_header(self, "Hostel Map", "Filter and sort by hostel, floor and status. Click a room for details, double-click for more.", fonts)
        bar = tk.Frame(self, bg=COLORS["background"])
        bar.pack(fill="x", padx=28, pady=(0, 8))
        self.vars = {"hostel": tk.StringVar(value=_ALL), "floor": tk.StringVar(value=_ALL),
                     "status": tk.StringVar(value=_ALL), "sort": tk.StringVar(value="Room number"),
                     "order": tk.StringVar(value="Top floor first")}
        self.combos = {}
        for key, label, values in (("hostel", "Hostel", [_ALL]), ("floor", "Floor", [_ALL]),
                                   ("status", "Status", [_ALL, "Vacant", "Partly full", "Full"]),
                                   ("sort", "Sort rooms", list(_SORTS)),
                                   ("order", "Floors", ["Top floor first", "Ground first"])):
            tk.Label(bar, text=label, bg=COLORS["background"], fg=COLORS["text_secondary"],
                     font=self.fonts["label"]).pack(side="left", padx=(0, 4))
            combo = ttk.Combobox(bar, textvariable=self.vars[key], values=values, state="readonly", width=15 if key == "sort" else 12)
            combo.pack(side="left", padx=(0, 12))
            combo.bind("<<ComboboxSelected>>", lambda e: self._render())
            self.combos[key] = combo
        self.show_facilities = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="Facilities", variable=self.show_facilities,
                        command=self._render).pack(side="left")
        legend = tk.Frame(self, bg=COLORS["background"])
        legend.pack(fill="x", padx=28, pady=(0, 8))
        for text, fg, bg in (("Vacant", COLORS["success"], COLORS["success_soft"]),
                             ("Partly full", COLORS["warning"], COLORS["warning_soft"]),
                             ("Full", COLORS["accent"], COLORS["accent_soft"])):
            chip(legend, text, fg, bg).pack(side="left", padx=(0, 6))
        self.scroll = ScrollFrame(self, bg=COLORS["background"])
        self.scroll.pack(fill="both", expand=True, padx=28, pady=(0, 6))
        self.detail = tk.Label(self, text="Click a room to see its details.", bg=COLORS["background"],
                               fg=COLORS["text_secondary"], font=fonts["body"], anchor="w", justify="left")
        self.detail.pack(fill="x", padx=28, pady=(0, 14))

    def refresh(self):
        self._rooms = home_service.floor_plan()
        self.combos["hostel"]["values"] = [_ALL] + sorted({r["hostel_type"] or "Unassigned" for r in self._rooms})
        self.combos["floor"]["values"] = [_ALL] + [_floor_name(f) for f in sorted({r["floor"] for r in self._rooms})]
        for key in ("hostel", "floor"):
            if self.vars[key].get() not in self.combos[key]["values"]:
                self.vars[key].set(_ALL)
        self._render()

    def _render(self):
        inner = self.scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        mine = home_service.my_room_number()
        if not self._rooms:
            tk.Label(inner, text="No rooms have been added yet.", bg=COLORS["background"],
                     fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(pady=20)
            return
        groups = {}
        for room in self._rooms:
            groups.setdefault(room["hostel_type"] or "Unassigned", {}).setdefault(room["floor"], []).append(room)
        wanted_hostel, wanted_floor = self.vars["hostel"].get(), self.vars["floor"].get()
        wanted_status = self.vars["status"].get()
        shown = 0
        for hostel, floors in groups.items():
            if wanted_hostel not in (_ALL, hostel):
                continue
            visible = {}
            for floor, rooms in floors.items():
                if wanted_floor not in (_ALL, _floor_name(floor)):
                    continue
                keep = [r for r in rooms if wanted_status in (_ALL, _status(r)[2])]
                if keep:
                    visible[floor] = sorted(keep, key=_SORTS[self.vars["sort"].get()])
            if visible:
                shown += 1
                self._building(inner, hostel, floors, visible, mine)
        if not shown:
            tk.Label(inner, text="No rooms match these filters.", bg=COLORS["background"],
                     fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(pady=20)
        self.scroll.update_scroll()

    def _building(self, parent, hostel, all_floors, visible, mine):
        members = [r for rooms in all_floors.values() for r in rooms]
        beds, taken = sum(r["capacity"] for r in members), sum(r["taken"] for r in members)
        percent = round(taken / beds * 100) if beds else 0
        card = Card(parent, fit=True)
        card.pack(fill="x", pady=(0, 14))
        body = card.body
        top = tk.Frame(body, bg=COLORS["surface"])
        top.pack(fill="x")
        tk.Label(top, text=_TITLES.get(hostel, "Rooms without a hostel set"), bg=COLORS["surface"],
                 fg=COLORS["text_primary"], font=self.fonts["section_title"]).pack(side="left")
        tk.Label(top, text=f"{len(members)} room{'s' if len(members) != 1 else ''} · {taken} of {beds} beds · {percent}%", bg=COLORS["surface"],
                 fg=COLORS["text_secondary"], font=self.fonts["label"]).pack(side="right")
        bar = tk.Canvas(body, height=8, bg=COLORS["surface"], highlightthickness=0)
        bar.pack(fill="x", pady=(6, 8))
        bar.bind("<Configure>", lambda e, b=bar, p=percent: self._draw_bar(b, p))
        ordered = sorted(visible, reverse=self.vars["order"].get() == "Top floor first")
        for floor in ordered:
            self._floor(body, floor, all_floors[floor], visible[floor], mine)

    def _floor(self, parent, floor, floor_rooms, rooms, mine):
        block = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
        block.pack(fill="x", pady=(0, 10))
        head = tk.Frame(block, bg=COLORS["surface"])
        head.pack(fill="x", padx=10, pady=(8, 6))
        beds = sum(r["capacity"] for r in floor_rooms)
        taken = sum(r["taken"] for r in floor_rooms)
        tk.Label(head, text=_floor_name(floor), bg=COLORS["surface"], fg=COLORS["text_primary"],
                 font=self.fonts["body_bold"]).pack(side="left")
        tk.Label(head, text=f"  {len(floor_rooms)} room{'s' if len(floor_rooms) != 1 else ''} · {taken}/{beds} beds", bg=COLORS["surface"],
                 fg=COLORS["text_secondary"], font=self.fonts["small"]).pack(side="left")
        if self.show_facilities.get():
            for name in reversed(_GROUND_FACILITIES if floor == 0 else _FLOOR_FACILITIES):
                color = COLORS[_FACILITY_COLORS[name]]
                chip(head, name, color, COLORS["background"]).pack(side="right", padx=(4, 0))
        grid = tk.Frame(block, bg=COLORS["surface"])
        grid.pack(fill="x", padx=6, pady=(0, 8))
        for col in range(_COLUMNS):
            grid.columnconfigure(col, weight=1, uniform="room")
        for i, room in enumerate(rooms):
            self._tile(grid, i // _COLUMNS, i % _COLUMNS, room, room["room_number"] == mine)

    def _draw_bar(self, bar, percent):
        bar.delete("all")
        w = max(bar.winfo_width(), 10)
        bar.create_rectangle(0, 0, w, 8, fill=COLORS["border"], outline="")
        if percent:
            bar.create_rectangle(0, 0, w * min(percent, 100) / 100, 8, fill=COLORS["accent"], outline="")

    def _tile(self, parent, row, column, room, is_mine):
        taken, cap = room["taken"], room["capacity"]
        fg, soft, label = _status(room)
        cell = tk.Frame(parent, bg=soft, padx=10, pady=8, cursor="hand2",
                        highlightthickness=2 if is_mine else 1,
                        highlightbackground=COLORS["text_primary"] if is_mine else COLORS["border"])
        cell.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
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

