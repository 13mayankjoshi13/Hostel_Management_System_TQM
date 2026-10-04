"""
Room Allocation screen. Same allocation_service pipeline as every prior
batch — only the presentation changed.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service, room_service, allocation_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, build_table, style_treeview_status_tags


class AllocationScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._student_options = {}
        self._room_options = {}
        section_header(self, "Room Allocation",
                        "Assign students to rooms and release when they move out.", fonts)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=28, pady=(18, 22))
        wrapper.columnconfigure(1, weight=1)

        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(wrapper, textvariable=self.student_var, state="readonly")
        form_row(wrapper, self.fonts, 0, "Student", self.student_combo)

        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(wrapper, textvariable=self.room_var, state="readonly")
        form_row(wrapper, self.fonts, 1, "Room", self.room_combo)

        button_row = tk.Frame(wrapper, bg=COLORS["background"])
        button_row.grid(row=2, column=1, sticky="w", pady=(10, 0))
        ttk.Button(button_row, text="Allocate", style="Primary.TButton",
                    command=self.on_allocate).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Lists", style="Secondary.TButton",
                    command=self.refresh_dropdowns).pack(side="left")

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        content = build_panel(wrapper, "Active Allocations", self.fonts)

        self.tree = build_table(content, ("id", "student", "room", "type", "allocated_at"),
                                  ("ID", "Student", "Room", "Type", "Allocated At"),
                                  (50, 190, 100, 100, 160), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

        ttk.Button(content, text="Release Selected", style="Danger.TButton",
                    command=self.on_release).pack(anchor="e", pady=(10, 0))

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
        for alloc in allocation_service.get_active_allocations():
            self.tree.insert("", "end", values=(
                alloc["allocation_id"], alloc["student_name"],
                alloc["room_number"], alloc["room_type"], alloc["allocated_at"],
            ), tags=("default",))

    def refresh(self):
        self.refresh_dropdowns()
        self.refresh_allocations()
