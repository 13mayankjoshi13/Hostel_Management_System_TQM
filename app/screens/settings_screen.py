"""Settings: appearance for everyone; audit log, student data download and Quality Monitoring for administrators."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.screens.quality_screen import QualityScreen
from app.services import audit_service, settings_service
from app.theme import (ACCENT_PRESETS, COLORS, Card, build_table, current_appearance, section_header,
                       style_treeview_status_tags)
from app.utils import session
from app.utils.exception_handler import handle_unexpected_error
from app.utils.validation import ValidationError


class SettingsScreen(tk.Frame):
    def __init__(self, parent, fonts, on_appearance_change=None):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        self._on_change = on_appearance_change or (lambda: None)
        self._tab = "appearance"
        section_header(self, "Settings", "Appearance, audit log, data download and quality tools.", fonts)
        self.tabs = tk.Frame(self, bg=COLORS["background"])
        self.tabs.pack(fill="x", padx=28, pady=(0, 10))
        self.tab_labels = {}
        self.body = tk.Frame(self, bg=COLORS["background"])
        self.body.pack(fill="both", expand=True, padx=28, pady=(0, 18))
        self.pages = {"appearance": self._build_appearance()}
        self.quality = None
        if session.get_role() in session.ADMIN_ROLES:
            self.pages["audit"] = self._build_audit()
            self.pages["data"] = self._build_data()
            self.quality = QualityScreen(self.body, fonts)
            self.pages["quality"] = self.quality
        labels = {"appearance": "Appearance", "audit": "Audit log", "data": "Data download",
                  "quality": "Quality Monitoring"}
        for key in self.pages:
            lbl = tk.Label(self.tabs, text=labels[key], font=fonts["section_title"], padx=12, pady=5, cursor="hand2")
            lbl.pack(side="left", padx=(0, 6))
            lbl.bind("<Button-1>", lambda e, k=key: self.show_tab(k))
            self.tab_labels[key] = lbl
        self.show_tab("appearance")

    def show_tab(self, key):
        self._tab = key
        for k, lbl in self.tab_labels.items():
            active = k == key
            lbl.configure(bg=COLORS["accent_soft"] if active else COLORS["background"],
                          fg=COLORS["accent"] if active else COLORS["text_secondary"])
        for page in self.pages.values():
            page.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        self._refresh_tab()

    def _card_page(self, title):
        card = Card(self.body, fit=False)
        tk.Label(card.body, text=title, bg=COLORS["surface"], fg=COLORS["text_primary"],
                 font=self.fonts["section_title"]).pack(anchor="w", pady=(0, 10))
        return card, card.body

    # ------------------------------------------------------ appearance
    def _build_appearance(self):
        card, body = self._card_page("Appearance")
        mode, accent = current_appearance()
        self.mode_var = tk.StringVar(value=mode)
        self.accent_var = tk.StringVar(value=accent)
        tk.Label(body, text="Theme", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 font=self.fonts["label"]).pack(anchor="w")
        row = tk.Frame(body, bg=COLORS["surface"])
        row.pack(anchor="w", pady=(4, 14))
        for m in settings_service.MODES:
            ttk.Radiobutton(row, text=m, value=m, variable=self.mode_var).pack(side="left", padx=(0, 16))
        tk.Label(body, text="Theme colour", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 font=self.fonts["label"]).pack(anchor="w")
        swatches = tk.Frame(body, bg=COLORS["surface"])
        swatches.pack(anchor="w", pady=(6, 10))
        for name, hex_color in ACCENT_PRESETS.items():
            cell = tk.Frame(swatches, bg=COLORS["surface"], cursor="hand2")
            cell.pack(side="left", padx=(0, 12))
            dot = tk.Canvas(cell, width=34, height=34, bg=COLORS["surface"], highlightthickness=0)
            dot.create_oval(3, 3, 31, 31, fill=hex_color, outline="")
            dot.pack()
            lbl = tk.Label(cell, text=name, bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["small"])
            lbl.pack()
            for w in (cell, dot, lbl):
                w.bind("<Button-1>", lambda e, c=hex_color: self.accent_var.set(c))
        custom = tk.Frame(body, bg=COLORS["surface"])
        custom.pack(anchor="w", pady=(4, 14))
        tk.Label(custom, text="Or type a colour (#RRGGBB)", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 font=self.fonts["label"]).pack(side="left", padx=(0, 8))
        ttk.Entry(custom, textvariable=self.accent_var, width=10).pack(side="left")
        ttk.Button(body, text="Apply", style="Primary.TButton", command=self.on_apply).pack(anchor="w")
        tk.Label(body, text="Saved for your account and used the next time you sign in on this computer.",
                 bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=self.fonts["label"]).pack(anchor="w", pady=(10, 0))
        return card

    def on_apply(self):
        try:
            settings_service.set_appearance(self.mode_var.get(), self.accent_var.get())
        except ValidationError as e:
            messagebox.showerror("Appearance", str(e))
            return
        except Exception as e:
            handle_unexpected_error("Settings", "set_appearance_ui", e)
            return
        self._on_change()

    # ------------------------------------------------------ audit log
    def _build_audit(self):
        card, body = self._card_page("Audit log")
        bar = tk.Frame(body, bg=COLORS["surface"])
        bar.pack(fill="x", pady=(0, 8))
        self.search_var = tk.StringVar()
        self.module_var = tk.StringVar(value="All")
        ttk.Entry(bar, textvariable=self.search_var, width=26).pack(side="left")
        self.module_box = ttk.Combobox(bar, textvariable=self.module_var, values=["All"], state="readonly", width=14)
        self.module_box.pack(side="left", padx=8)
        ttk.Button(bar, text="Search", style="Secondary.TButton", command=self._refresh_audit).pack(side="left")
        self.audit_tree = build_table(body, ("time", "user", "role", "module", "action", "result", "description"),
                                      ("Time", "User", "Role", "Module", "Action", "Result", "Description"),
                                      (130, 80, 90, 80, 80, 70, 320), height=14)
        self.audit_tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.audit_tree)
        self.audit_tree.tag_configure("failure", foreground=COLORS["danger"])
        return card

    def _refresh_audit(self):
        try:
            self.module_box["values"] = ["All"] + audit_service.audit_modules()
            module = "" if self.module_var.get() == "All" else self.module_var.get()
            rows = audit_service.read_audit_log(self.search_var.get(), module)
        except ValidationError as e:
            messagebox.showerror("Audit log", str(e))
            return
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        for r in rows:
            tag = "failure" if r.get("result") == "Failure" else "default"
            self.audit_tree.insert("", "end", values=(
                r.get("timestamp", ""), r.get("user_id", ""), r.get("role", ""), r.get("module", ""),
                r.get("action", ""), r.get("result", ""), r.get("description", "")), tags=(tag,))

    # ------------------------------------------------------ data download
    def _build_data(self):
        card, body = self._card_page("Data download")
        tk.Label(body, text="Download every student record (name, registration number, contact, gender, "
                            "current room) as a CSV file you can open in Excel. Each download is recorded in the audit log.",
                 bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["body"], wraplength=620,
                 justify="left").pack(anchor="w", pady=(0, 12))
        ttk.Button(body, text="Download student data", style="Primary.TButton",
                   command=self.on_download).pack(anchor="w")
        return card

    def on_download(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="students.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        try:
            count = audit_service.export_students_csv(path)
            messagebox.showinfo("Download complete", f"Saved {count} student record(s).")
        except ValidationError as e:
            messagebox.showerror("Download", str(e))
        except Exception as e:
            handle_unexpected_error("Student", "download_students_ui", e)

    def _refresh_tab(self):
        if self._tab == "audit":
            self._refresh_audit()
        elif self._tab == "quality" and self.quality is not None:
            self.quality.refresh()

    def refresh(self):
        self._refresh_tab()
