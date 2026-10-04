"""
Room Management screen. Same room_service calls as every prior batch —
only the presentation changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import room_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags


class RoomScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Rooms", "Manage rooms, types, and capacity.", fonts)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)

        self.room_no_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Single")
        self.capacity_var = tk.StringVar()

        form_row(wrapper, self.fonts, 0, "Room No.", ttk.Entry(wrapper, textvariable=self.room_no_var))
        form_row(wrapper, self.fonts, 1, "Type", ttk.Combobox(
            wrapper, textvariable=self.type_var,
            values=["Single", "Double", "Triple", "Dormitory"], state="readonly"))
        form_row(wrapper, self.fonts, 2, "Capacity", ttk.Entry(wrapper, textvariable=self.capacity_var))

        ttk.Button(wrapper, text="Add Room", style="Primary.TButton",
                    command=self.on_add).grid(row=3, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "All Rooms", self.fonts)

        self.tree = build_table(content, ("id", "room_no", "type", "capacity"),
                                  ("ID", "Room No.", "Type", "Capacity"),
                                  (50, 150, 150, 100), height=10)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

    def on_add(self):
        try:
            room_service.add_room(
                self.room_no_var.get(), self.type_var.get(), self.capacity_var.get()
            )
            self.room_no_var.set("")
            self.capacity_var.set("")
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
            ), tags=("default",))
