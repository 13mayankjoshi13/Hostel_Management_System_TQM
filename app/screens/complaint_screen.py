"""
Complaint Management screen.

Status flow enforced by complaint_service (Open -> Assigned -> Resolved,
or Open -> Resolved directly): this screen just calls the service and
shows a status badge per row; it never decides transitions itself.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.services import student_service, complaint_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, build_card, build_breadcrumb, style_treeview_stripes, stripe_tag

_CATEGORIES = ["Maintenance", "Cleanliness", "Noise", "Security", "Food", "Other"]


class ComplaintScreen(tk.Frame):
    def __init__(self, parent, fonts, go_home=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self.go_home = go_home
        self._student_options = {}
        self._complaint_rows = {}   # tree item id -> complaint dict
        self._build_header()
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header_bg"])
        header.pack(fill="x")
        if self.go_home:
            build_breadcrumb(header, "Complaints", self.go_home, self.fonts)
        inner = tk.Frame(header, bg=COLORS["header_bg"])
        inner.pack(fill="x", padx=24, pady=16)
        tk.Label(inner, text="Complaint Management", bg=COLORS["header_bg"],
                  fg=COLORS["text_dark"], font=self.fonts["header"]).pack(anchor="w")
        tk.Label(inner, text="Log, assign, and resolve hosteller complaints.",
                  bg=COLORS["header_bg"], fg=COLORS["text_muted"],
                  font=self.fonts["subheader"]).pack(anchor="w")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

    def _build_form(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=24, pady=(16, 0))
        content = build_card(wrapper, "Log a Complaint", self.fonts)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Student", style="FormLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(content, textvariable=self.student_var, state="readonly")
        self.student_combo.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Category", style="FormLabel.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.category_var = tk.StringVar(value=_CATEGORIES[0])
        ttk.Combobox(content, textvariable=self.category_var, values=_CATEGORIES,
                      state="readonly").grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Description", style="FormLabel.TLabel").grid(
            row=2, column=0, sticky="nw", pady=6, padx=(0, 12))
        self.description_text = tk.Text(content, height=3, wrap="word",
                                          font=self.fonts["body"], relief="solid", bd=1,
                                          bg=COLORS["surface_alt"], fg=COLORS["text_light"],
                                          insertbackground=COLORS["text_light"],
                                          highlightbackground=COLORS["border"],
                                          highlightcolor=COLORS["primary"])
        self.description_text.grid(row=2, column=1, sticky="ew", pady=6)

        button_row = tk.Frame(content, bg=COLORS["card_bg"])
        button_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(button_row, text="+  Log Complaint", style="Primary.TButton",
                    command=self.on_create).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Students", style="Secondary.TButton",
                    command=self.refresh_student_dropdown).pack(side="left")

    def _build_table(self):
        wrapper = tk.Frame(self, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content = build_card(wrapper, "All Complaints", self.fonts)

        columns = ("id", "student", "category", "status", "assigned_to", "created_at")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=6)
        for col, label, width in zip(
            columns, ("ID", "Student", "Category", "Status", "Assigned To", "Created At"),
            (45, 160, 110, 90, 140, 150),
        ):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        style_treeview_stripes(self.tree)
        self.tree.tag_configure("status_open", foreground="#D97706")
        self.tree.tag_configure("status_assigned", foreground="#2563EB")
        self.tree.tag_configure("status_resolved", foreground="#059669")

        button_row = tk.Frame(content, bg=COLORS["card_bg"])
        button_row.pack(anchor="e", pady=(10, 0))
        ttk.Button(button_row, text="Assign Selected", style="Secondary.TButton",
                    command=self.on_assign).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Resolve Selected", style="Primary.TButton",
                    command=self.on_resolve).pack(side="left")

    def refresh_student_dropdown(self):
        self._student_options = {
            f"{s['student_id']} — {s['name']} ({s['registration_number']})": s["student_id"]
            for s in student_service.get_all_students()
        }
        self.student_combo["values"] = list(self._student_options.keys())

    def on_create(self):
        student_label = self.student_var.get()
        if not student_label:
            messagebox.showerror("Invalid Input", "Please select a student.")
            return
        student_id = self._student_options.get(student_label)
        description = self.description_text.get("1.0", "end").strip()

        try:
            complaint_service.create_complaint(student_id, self.category_var.get(), description)
            self.description_text.delete("1.0", "end")
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint logged successfully.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "create_complaint_ui", e)

    def _get_selected_complaint(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a complaint first.")
            return None
        return self._complaint_rows.get(selected[0])

    def on_assign(self):
        complaint = self._get_selected_complaint()
        if complaint is None:
            return
        assigned_to = simpledialog.askstring(
            "Assign Complaint", "Assign to (staff name):", parent=self
        )
        if assigned_to is None:
            return
        try:
            complaint_service.assign_complaint(complaint["complaint_id"], assigned_to)
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint assigned.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "assign_complaint_ui", e)

    def on_resolve(self):
        complaint = self._get_selected_complaint()
        if complaint is None:
            return
        notes = simpledialog.askstring(
            "Resolve Complaint", "Resolution notes:", parent=self
        )
        if notes is None:
            return
        try:
            complaint_service.resolve_complaint(complaint["complaint_id"], notes)
            self.refresh_table()
            messagebox.showinfo("Success", "Complaint resolved.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Complaint", "resolve_complaint_ui", e)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._complaint_rows = {}
        status_tag = {"Open": "status_open", "Assigned": "status_assigned",
                       "Resolved": "status_resolved"}
        for i, complaint in enumerate(complaint_service.get_all_complaints()):
            tags = (stripe_tag(i), status_tag.get(complaint["status"], ""))
            item_id = self.tree.insert("", "end", values=(
                complaint["complaint_id"], complaint["student_name"], complaint["category"],
                complaint["status"], complaint["assigned_to"] or "—", complaint["created_at"],
            ), tags=tags)
            self._complaint_rows[item_id] = complaint

    def refresh(self):
        self.refresh_student_dropdown()
        self.refresh_table()
