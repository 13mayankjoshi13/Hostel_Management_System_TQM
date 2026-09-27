"""
Tkinter GUI foundation.

Kept intentionally simple (Notebook with Students, Rooms, and Allocation
tabs). Every form submission goes through the service layer, so
validation and logging happen the same way here as they would from any
other future interface (e.g. a web UI).

Error-handling pattern used everywhere in this file:

    try:
        service.do_something(...)
    except ValidationError as e:
        messagebox.showerror("Invalid Input", str(e))   # expected, friendly
    except Exception as e:
        # unexpected -> central handler logs it and shows a generic message
        handle_unexpected_error(...)
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_service, room_service, allocation_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.config import APP_NAME


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("820x520")
        self.minsize(700, 460)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.student_tab = StudentTab(notebook)
        self.room_tab = RoomTab(notebook)
        self.allocation_tab = AllocationTab(notebook)

        notebook.add(self.student_tab, text="Students")
        notebook.add(self.room_tab, text="Rooms")
        notebook.add(self.allocation_tab, text="Room Allocation")

        # Allocation dropdowns need fresh student/room lists whenever this
        # tab becomes visible, in case one was just added on another tab.
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        notebook = event.widget
        if notebook.select() == str(self.allocation_tab):
            self.allocation_tab.refresh_dropdowns()


class StudentTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        form = ttk.LabelFrame(self, text="Add Student")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Registration No.:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.reg_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.reg_var, width=30).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Contact No.:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.contact_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.contact_var, width=30).grid(row=2, column=1, padx=4, pady=4)

        ttk.Button(form, text="Add Student", command=self.on_add).grid(
            row=3, column=0, columnspan=2, pady=8
        )

        list_frame = ttk.LabelFrame(self, text="Students")
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("id", "name", "reg_no", "contact")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col, label in zip(columns, ("ID", "Name", "Registration No.", "Contact")):
            self.tree.heading(col, text=label)
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.refresh()

    def on_add(self):
        try:
            student_service.add_student(
                self.name_var.get(), self.reg_var.get(), self.contact_var.get()
            )
            self.name_var.set("")
            self.reg_var.set("")
            self.contact_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Student added successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Student", "add_student_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in student_service.get_all_students():
            self.tree.insert("", "end", values=(
                student["student_id"], student["name"],
                student["registration_number"], student["contact_number"],
            ))


class RoomTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        form = ttk.LabelFrame(self, text="Add Room")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Room No.:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.room_no_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.room_no_var, width=20).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Type:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.type_var = tk.StringVar(value="Single")
        ttk.Combobox(
            form, textvariable=self.type_var,
            values=["Single", "Double", "Triple", "Dormitory"],
            state="readonly", width=18,
        ).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Capacity:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.capacity_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.capacity_var, width=20).grid(row=2, column=1, padx=4, pady=4)

        ttk.Button(form, text="Add Room", command=self.on_add).grid(
            row=3, column=0, columnspan=2, pady=8
        )

        list_frame = ttk.LabelFrame(self, text="Rooms")
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("id", "room_no", "type", "capacity")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col, label in zip(columns, ("ID", "Room No.", "Type", "Capacity")):
            self.tree.heading(col, text=label)
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.refresh()

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
            ))


class AllocationTab(ttk.Frame):
    """
    Room Allocation tab. Dropdowns show "ID — label" so the underlying ID
    can be recovered even though the visible text is human-readable.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._student_options = {}   # display string -> student_id
        self._room_options = {}      # display string -> room_id

        form = ttk.LabelFrame(self, text="Allocate Room")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Student:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(
            form, textvariable=self.student_var, state="readonly", width=40
        )
        self.student_combo.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Room:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(
            form, textvariable=self.room_var, state="readonly", width=40
        )
        self.room_combo.grid(row=1, column=1, padx=4, pady=4)

        button_row = ttk.Frame(form)
        button_row.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(button_row, text="Allocate", command=self.on_allocate).pack(side="left", padx=4)
        ttk.Button(button_row, text="Refresh Lists", command=self.refresh_dropdowns).pack(side="left", padx=4)

        list_frame = ttk.LabelFrame(self, text="Active Allocations")
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("id", "student", "room", "type", "allocated_at")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col, label in zip(columns, ("ID", "Student", "Room", "Type", "Allocated At")):
            self.tree.heading(col, text=label)
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        ttk.Button(list_frame, text="Release Selected", command=self.on_release).pack(
            anchor="e", padx=4, pady=4
        )

        self.refresh_dropdowns()
        self.refresh_allocations()

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
            ))
