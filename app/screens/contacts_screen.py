"""Warden details and emergency numbers. Everyone reads; administrators edit."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import emergency_service, warden_service
from app.utils import session
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, Card, ScrollFrame, section_header, build_panel, build_table, form_card, form_row, split_layout, button_row


class ContactsScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Wardens & Emergency", "Who to contact, and numbers to call in an emergency.", fonts)
        self.left, self.right = split_layout(self)
        self.warden_vars = {k: tk.StringVar() for k in ("name", "gender", "contact", "hostel", "hours")}
        self.number_vars = {k: tk.StringVar() for k in ("name", "number")}
        self.number_vars["category"] = tk.StringVar(value="University")

        self.left_scroll = ScrollFrame(self.left, bg=COLORS["background"])
        self.left_scroll.pack(fill="both", expand=True)
        self.form_host = self.left_scroll.inner
        self._build_forms()

        self.warden_tree = build_table(build_panel(self._half(), "Wardens", fonts),
                                       ("id", "name", "gender", "contact", "hostel", "hours"),
                                       ("ID", "Name", "Gender", "Contact", "Hostel", "Office hours"),
                                       (40, 130, 60, 110, 100, 100), height=4)
        self.warden_tree.pack(fill="both", expand=True)

        def _on_warden_select(e=None):
            sel = self.warden_tree.selection()
            if not sel: return
            vals = self.warden_tree.item(sel[0], "values")
            if vals:
                if session.get_role() in session.ADMIN_ROLES:
                    self.warden_vars["name"].set(vals[1])
                    self.warden_vars["gender"].set(vals[2])
                    self.warden_vars["contact"].set(vals[3])
                    self.warden_vars["hostel"].set(vals[4])
                    self.warden_vars["hours"].set(vals[5] if vals[5] != "—" else "")
                from app.theme import show_detail_dialog
                show_detail_dialog(
                    parent=self,
                    title=f"Warden: {vals[1]}",
                    subtitle="Hostel Administration",
                    icon="user",
                    color=COLORS["accent"],
                    fields=[
                        ("Warden ID", vals[0]),
                        ("Name", vals[1]),
                        ("Gender", vals[2]),
                        ("Contact", vals[3]),
                        ("Hostel", vals[4]),
                        ("Office Hours", vals[5]),
                    ],
                    full_text=f"Warden {vals[1]} manages {vals[4]}. Contact: {vals[3]}. Office hours: {vals[5]}."
                )
        self.warden_tree.bind("<Double-Button-1>", _on_warden_select)
        self.warden_tree.bind("<Return>", _on_warden_select)

        self.number_tree = build_table(build_panel(self._half(), "Emergency numbers & University Helplines", fonts),
                                       ("id", "name", "number", "category"),
                                       ("ID", "Service / Department", "Number / Email", "Category"), (40, 190, 150, 90), height=6)
        self.number_tree.pack(fill="both", expand=True)

        def _on_num_select(e=None):
            sel = self.number_tree.selection()
            if not sel: return
            vals = self.number_tree.item(sel[0], "values")
            if vals:
                if session.get_role() in session.ADMIN_ROLES:
                    self.number_vars["name"].set(vals[1])
                    self.number_vars["number"].set(vals[2])
                    self.number_vars["category"].set(vals[3])

                from app.theme import show_detail_dialog
                show_detail_dialog(
                    parent=self,
                    title=f"Emergency: {vals[1]}",
                    subtitle="University & Emergency Contact",
                    icon="chat",
                    color=COLORS["accent"],
                    fields=[
                        ("Contact ID", vals[0]),
                        ("Service / Department", vals[1]),
                        ("Phone / Email", vals[2]),
                        ("Category", vals[3]),
                    ],
                    full_text=f"Official contact for {vals[1]} ({vals[3]}). Number/Email: {vals[2]}."
                )
        self.number_tree.bind("<Double-Button-1>", _on_num_select)
        self.number_tree.bind("<Return>", _on_num_select)

    def _half(self):
        frame = tk.Frame(self.right, bg=COLORS["background"])
        frame.pack(fill="both", expand=True, pady=(0, 10))
        return frame

    def _build_forms(self):
        f = self.fonts
        w = form_card(self.form_host, "Add a warden", f)
        v = self.warden_vars
        form_row(w, f, 0, "Name", ttk.Entry(w, textvariable=v["name"]))
        form_row(w, f, 1, "Gender", ttk.Combobox(w, textvariable=v["gender"], values=["Male", "Female"], state="readonly"))
        form_row(w, f, 2, "Contact No.", ttk.Entry(w, textvariable=v["contact"]))
        form_row(w, f, 3, "Hostel", ttk.Entry(w, textvariable=v["hostel"]))
        form_row(w, f, 4, "Office hours", ttk.Entry(w, textvariable=v["hours"]))
        b = button_row(w, 5)
        ttk.Button(b, text="Add Warden", style="Primary.TButton", command=self.on_add_warden).pack(side="left")
        ttk.Button(b, text="Remove Selected", style="Secondary.TButton",
                   command=self.on_remove_warden).pack(side="left", padx=(8, 0))

        n = form_card(self.form_host, "Emergency & University Contact", f)
        form_row(n, f, 0, "Service / Dept", ttk.Entry(n, textvariable=self.number_vars["name"]))
        form_row(n, f, 1, "Number / Email", ttk.Entry(n, textvariable=self.number_vars["number"]))
        form_row(n, f, 2, "Category", ttk.Entry(n, textvariable=self.number_vars["category"]))
        b2 = button_row(n, 3)
        ttk.Button(b2, text="Add Contact", style="Primary.TButton", command=self.on_add_number).pack(side="left")
        ttk.Button(b2, text="Update Selected", style="Secondary.TButton", command=self.on_update_number).pack(side="left", padx=(8, 0))
        ttk.Button(b2, text="Remove Selected", style="Secondary.TButton",
                   command=self.on_remove_number).pack(side="left", padx=(8, 0))

    def _run(self, action, label, done=None):
        try:
            action()
            self.refresh()
            if done:
                done()
        except ValidationError as e:
            messagebox.showerror(label, str(e))
        except Exception as e:
            handle_unexpected_error("Contacts", label, e)

    def on_add_warden(self):
        v = self.warden_vars
        self._run(lambda: warden_service.add_warden(v["name"].get(), v["gender"].get(), v["contact"].get(),
                                                    v["hostel"].get(), v["hours"].get()), "add_warden_ui",
                  lambda: [x.set("") for x in v.values()])

    def on_add_number(self):
        v = self.number_vars
        self._run(lambda: emergency_service.add_contact(v["name"].get(), v["number"].get(), v["category"].get()),
                  "add_number_ui", lambda: (v["name"].set(""), v["number"].set("")))

    def on_update_number(self):
        cid = self._selected(self.number_tree, "number")
        if cid is not None:
            v = self.number_vars
            self._run(lambda: emergency_service.update_contact(int(cid), v["name"].get(), v["number"].get(), v["category"].get()),
                      "update_number_ui", lambda: (v["name"].set(""), v["number"].set("")))

    def _selected(self, tree, label):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("No Selection", f"Select a {label} first.")
            return None
        return tree.item(selected[0])["values"][0]

    def on_remove_warden(self):
        wid = self._selected(self.warden_tree, "warden")
        if wid is not None:
            self._run(lambda: warden_service.delete_warden(wid), "remove_warden_ui")

    def on_remove_number(self):
        cid = self._selected(self.number_tree, "number")
        if cid is not None:
            self._run(lambda: emergency_service.delete_contact(cid), "remove_number_ui")

    def refresh(self):
        is_admin = session.get_role() in session.ADMIN_ROLES
        if is_admin:
            self.left_scroll.pack(fill="both", expand=True)
        else:
            self.left_scroll.pack_forget()
        for tree in (self.warden_tree, self.number_tree):
            for row in tree.get_children():
                tree.delete(row)
        if session.get_role() == "Student":
            mine = warden_service.warden_for_student()
            wardens = [mine] if mine else []
        else:
            wardens = warden_service.list_wardens()
        for w in wardens:
            self.warden_tree.insert("", "end", values=(w["warden_id"], w["name"], w["gender"], w["contact_number"],
                                                        w["hostel_name"], w["office_hours"] or "—"), tags=("default",))
        for c in emergency_service.list_contacts():
            self.number_tree.insert("", "end", values=(c["contact_id"], c["name"], c["number"], c["category"]),
                                    tags=("default",))
        if hasattr(self, "left_scroll"):
            self.left_scroll.update_scroll()
