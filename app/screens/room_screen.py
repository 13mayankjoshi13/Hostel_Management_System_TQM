"""
Room Management screen. Same room_service calls as every prior batch —
only the presentation changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import room_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags, form_card, split_layout


class RoomScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Rooms", "Manage rooms, types, and capacity.", fonts)
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Add a room", self.fonts)

        self.room_no_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Single")
        self.capacity_var = tk.StringVar()
        self.floor_var = tk.StringVar(value="0")
        self.hostel_var = tk.StringVar()

        form_row(wrapper, self.fonts, 0, "Room No.", ttk.Entry(wrapper, textvariable=self.room_no_var))
        form_row(wrapper, self.fonts, 1, "Type", ttk.Combobox(
            wrapper, textvariable=self.type_var,
            values=["Single", "Double", "Triple", "Dormitory"], state="readonly"))
        form_row(wrapper, self.fonts, 2, "Capacity", ttk.Entry(wrapper, textvariable=self.capacity_var))

        form_row(wrapper, self.fonts, 3, "Floor (0 = ground)", ttk.Entry(wrapper, textvariable=self.floor_var))
        form_row(wrapper, self.fonts, 4, "Hostel", ttk.Combobox(
            wrapper, textvariable=self.hostel_var, values=["", "Boys", "Girls"], state="readonly"))

        ttk.Button(wrapper, text="Add Room", style="Primary.TButton",
                    command=self.on_add).grid(row=5, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self.right, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)
        content = build_panel(wrapper, "All Rooms", self.fonts)

        self.tree = build_table(content, ("id", "room_no", "type", "capacity", "floor", "hostel"),
                                  ("ID", "Room No.", "Type", "Capacity", "Floor", "Hostel"),
                                  (50, 110, 110, 80, 60, 80), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

    def on_add(self):
        try:
            room_service.add_room(
                self.room_no_var.get(), self.type_var.get(), self.capacity_var.get(),
                self.floor_var.get(), self.hostel_var.get() or None
            )
            self.room_no_var.set("")
            self.capacity_var.set("")
            self.floor_var.set("0")
            self.refresh()
            messagebox.showinfo("Success", "Room added successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Room", "add_room_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for room in room_service.get_all_rooms():
            self.tree.insert("", "end", values=(
                room["room_id"], room["room_number"], room["room_type"], room["capacity"],
                room["floor"], room["hostel_type"] or "—",
            ), tags=("default",))
