"""User Management screen (Administrator only)."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.services import auth_service, student_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, build_panel, form_card, split_layout

_ROLES = ["Administrator", "Warden", "Staff", "Student"]


class UserScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._rows = {}
        self._student_options = {}
        section_header(self, "User Management",
                        "Create accounts, reset passwords and remove access.", fonts)
        self.left, self.right = split_layout(self)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        wrapper = form_card(self.left, "Create an account", self.fonts)

        self.username_var = tk.StringVar()
        form_row(wrapper, self.fonts, 0, "Username", ttk.Entry(wrapper, textvariable=self.username_var))

        self.password_var = tk.StringVar()
        form_row(wrapper, self.fonts, 1, "Password",
                 ttk.Entry(wrapper, textvariable=self.password_var, show="•"))

        self.role_var = tk.StringVar(value=_ROLES[1])
        form_row(wrapper, self.fonts, 2, "Role", ttk.Combobox(
            wrapper, textvariable=self.role_var, values=_ROLES, state="readonly"))

        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(wrapper, textvariable=self.student_var, state="readonly")
        form_row(wrapper, self.fonts, 3, "Student (Student role)", self.student_combo)

        ttk.Button(wrapper, text="Create Account", style="Primary.TButton",
                    command=self.on_create).grid(row=4, column=1, sticky="w", pady=(10, 0))

    def _build_table(self):
        wrapper = tk.Frame(self.right, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True)
        content = build_panel(wrapper, "Accounts", self.fonts)

        columns = ("id", "username", "role", "student", "created")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=8)
        for col, label, width in zip(columns, ("ID", "Username", "Role", "Linked student", "Created"),
                                      (50, 160, 110, 160, 160)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)

        button_row = tk.Frame(content, bg=COLORS["surface"])
        button_row.pack(anchor="e", pady=(10, 0))
        ttk.Button(button_row, text="Change Password", style="Secondary.TButton",
                    command=self.on_change_password).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Delete Account", style="Secondary.TButton",
                    command=self.on_delete).pack(side="left")

    def on_create(self):
        try:
            student_id = self._student_options.get(self.student_var.get())
            auth_service.create_user(self.username_var.get(), self.password_var.get(),
                                      self.role_var.get(), student_id if self.role_var.get() == "Student" else None)
            self.username_var.set("")
            self.password_var.set("")
            self.student_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Account created.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("User", "create_user_ui", e)

    def _selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select an account first.")
            return None
        return self._rows.get(selected[0])

    def on_change_password(self):
        user = self._selected()
        if user is None:
            return
        new_password = simpledialog.askstring(
            "Change Password", f"New password for '{user['username']}':", parent=self, show="•")
        if new_password is None:
            return
        try:
            auth_service.change_password(user["user_id"], new_password)
            messagebox.showinfo("Success", "Password changed.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("User", "change_password_ui", e)

    def on_delete(self):
        user = self._selected()
        if user is None:
            return
        if not messagebox.askyesno("Delete Account", f"Delete '{user['username']}'?"):
            return
        try:
            auth_service.delete_user(user["user_id"])
            self.refresh()
            messagebox.showinfo("Success", "Account deleted.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("User", "delete_user_ui", e)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._rows = {}
        users = auth_service.list_users()
        linked = {u["student_id"] for u in users if u["student_id"] is not None}
        self._student_options = {
            f"{s['name']} ({s['registration_number']})": s["student_id"]
            for s in student_service.get_all_students() if s["student_id"] not in linked
        }
        self.student_combo["values"] = list(self._student_options.keys())
        for user in users:
            item = self.tree.insert("", "end", values=(
                user["user_id"], user["username"], user["role"],
                user["student_name"] or "—", user["created_at"]))
            self._rows[item] = user
