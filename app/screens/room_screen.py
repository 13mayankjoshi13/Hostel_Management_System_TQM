"""
Room Management screen. Same room_service calls as before Batch 3 —
presentation only changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import room_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_card, style_treeview_stripes, stripe_tag


class RoomScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._build_header()
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=16)
        tk.Label(inner, text="Room Management", bg=COLORS["header_bg"],
                  fg=COLORS["text_dark"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Add rooms and track capacity.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=24, pady=(16, 0))
        content = build_card(wrapper, "Add Room", self.fonts)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Room No.", style="FormLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.room_no_var = tk.StringVar()
        ttk.Entry(content, textvariable=self.room_no_var).grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Type", style="FormLabel.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.type_var = tk.StringVar(value="Single")
        ttk.Combobox(content, textvariable=self.type_var,
                      values=["Single", "Double", "Triple", "Dormitory"],
                      state="readonly").grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Capacity", style="FormLabel.TLabel").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        self.capacity_var = tk.StringVar()
        ttk.Entry(content, textvariable=self.capacity_var).grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Button(content, text="+  Add Room", style="Primary.TButton",
                    command=self.on_add).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content = build_card(wrapper, "All Rooms", self.fonts)

        columns = ("id", "room_no", "type", "capacity")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        for col, label, width in zip(columns, ("ID", "Room No.", "Type", "Capacity"),
                                       (50, 140, 140, 100)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_stripes(self.tree)

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
        for i, room in enumerate(room_service.get_all_rooms()):
            self.tree.insert("", "end", values=(
                room["room_id"], room["room_number"], room["room_type"], room["capacity"],
            ), tags=(stripe_tag(i),))
