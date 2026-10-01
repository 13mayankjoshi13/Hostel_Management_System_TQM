"""
Room Allocation screen. Same allocation_service pipeline as before
Batch 3 (Select Student -> Check Student -> Select Room -> Check Room
Exists -> Check Capacity -> Check Existing Allocation -> Allocate) —
presentation only changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service, room_service, allocation_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_card, build_breadcrumb, style_treeview_stripes, stripe_tag


class AllocationScreen(tk.Frame):
    def __init__(self, parent, fonts, go_home=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self.go_home = go_home
        self._student_options = {}
        self._room_options = {}
        self._build_header()
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        if self.go_home:
            build_breadcrumb(header, "Room Allocation", self.go_home, self.fonts)
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=16)
        tk.Label(inner, text="Room Allocation", bg=COLORS["header_bg"],
                  fg=COLORS["text_dark"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Assign students to rooms and release when they move out.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=24, pady=(16, 0))
        content = build_card(wrapper, "Allocate Room", self.fonts)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Student", style="FormLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(content, textvariable=self.student_var, state="readonly")
        self.student_combo.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Room", style="FormLabel.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(content, textvariable=self.room_var, state="readonly")
        self.room_combo.grid(row=1, column=1, sticky="ew", pady=6)

        button_row = tk.Frame(content, bg=COLORS["card_bg"])
        button_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(button_row, text="Allocate", style="Primary.TButton",
                    command=self.on_allocate).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Lists", style="Secondary.TButton",
                    command=self.refresh_dropdowns).pack(side="left")

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content = build_card(wrapper, "Active Allocations", self.fonts)

        columns = ("id", "student", "room", "type", "allocated_at")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=6)
        for col, label, width in zip(columns, ("ID", "Student", "Room", "Type", "Allocated At"),
                                       (50, 180, 100, 100, 160)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        style_treeview_stripes(self.tree)

        # Pack the button to the bottom FIRST, then let the tree fill the
        # remaining space above it. Packing the tree first with
        # expand=True can claim all available space in a fixed-size
        # parent (these screens are placed with relwidth/relheight=1),
        # leaving nothing for a widget packed after it.
        ttk.Button(content, text="Release Selected", style="Danger.TButton",
                    command=self.on_release).pack(side="bottom", anchor="e", pady=(10, 0))
        self.tree.pack(fill="both", expand=True)

    def refresh_dropdowns(self):
        self._student_options = {
            f"{s['student_id']} — {s['name']} ({s['registration_number']})": s["student_id"]
            for s in student_service.get_all_students()
        }
        self._room_options = {
            f"{r['room_id']} — {r['room_number']} ({r['room_type']}, cap {r['capacity']})": r["room_id"]
            for r in room_service.get_all_rooms()
        }
        self.student_combo["values"] = list(self._student_options.keys())
        self.room_combo["values"] = list(self._room_options.keys())

    def on_allocate(self):
        student_label = self.student_var.get()
        room_label = self.room_var.get()
        if not student_label or not room_label:
            messagebox.showerror("Invalid Input", "Please select both a student and a room.")
            return

        student_id = self._student_options.get(student_label)
        room_id = self._room_options.get(room_label)
        try:
            allocation_service.allocate_room(student_id, room_id)
            self.student_var.set("")
            self.room_var.set("")
            self.refresh_allocations()
            messagebox.showinfo("Success", "Room allocated successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Allocation", "allocate_room_ui", e)

    def on_release(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select an allocation to release first.")
            return
        allocation_id = self.tree.item(selected[0])["values"][0]
        try:
            allocation_service.release_allocation(allocation_id)
            self.refresh_allocations()
            messagebox.showinfo("Success", "Allocation released.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Allocation", "release_allocation_ui", e)

    def refresh_allocations(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, alloc in enumerate(allocation_service.get_active_allocations()):
            self.tree.insert("", "end", values=(
                alloc["allocation_id"], alloc["student_name"],
                alloc["room_number"], alloc["room_type"], alloc["allocated_at"],
            ), tags=(stripe_tag(i),))

    def refresh(self):
        self.refresh_dropdowns()
        self.refresh_allocations()
