"""Workers screen (staff): registry, daily attendance and workload."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import worker_service
from app.utils.validation import ValidationError, WORKER_TRADES
from app.utils.exception_handler import handle_unexpected_error
from app.theme import (keep_selection, COLORS, status_tag, section_header, form_row, build_panel, build_table,
                       style_treeview_status_tags, form_card, split_layout)


class WorkerScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Workers", "Cleaners, electricians, plumbers and other hostel staff: attendance and jobs.", fonts)
        self.left, self.right = split_layout(self)

        wrapper = form_card(self.left, "Add a worker", fonts)
        self.name_var = tk.StringVar()
        form_row(wrapper, fonts, 0, "Name", ttk.Entry(wrapper, textvariable=self.name_var))
        self.trade_var = tk.StringVar(value=WORKER_TRADES[0])
        form_row(wrapper, fonts, 1, "Role", ttk.Combobox(wrapper, textvariable=self.trade_var,
                                                         values=list(WORKER_TRADES), state="readonly"))
        self.contact_var = tk.StringVar()
        form_row(wrapper, fonts, 2, "Contact number", ttk.Entry(wrapper, textvariable=self.contact_var))
        ttk.Button(wrapper, text="Add Worker", style="Primary.TButton",
                    command=self.on_add).grid(row=3, column=1, sticky="w", pady=(10, 0))

        table_wrapper = tk.Frame(self.right, bg=COLORS["background"])
        table_wrapper.pack(fill="both", expand=True)
        content = build_panel(table_wrapper, "Workers", fonts)
        self.tree = build_table(content, ("id", "name", "role", "contact", "status", "today", "open", "done"),
                                  ("ID", "Name", "Role", "Contact", "Status", "Today", "Open jobs", "Done"),
                                  (40, 130, 85, 95, 65, 80, 70, 45), height=7)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        buttons = tk.Frame(content, bg=COLORS["surface"])
        buttons.pack(anchor="e", pady=(10, 0))
        for label, status in (("Present", "Present"), ("Absent", "Absent"), ("On Leave", "On Leave")):
            ttk.Button(buttons, text=label, style="Secondary.TButton",
                        command=lambda s=status: self._act(lambda i: worker_service.mark_attendance(i, s),
                                                           f"Marked {s.lower()} for today.")).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Deactivate", style="Secondary.TButton",
                    command=lambda: self._act(lambda i: worker_service.set_worker_active(i, False),
                                              "Worker deactivated.")).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Reactivate", style="Secondary.TButton",
                    command=lambda: self._act(lambda i: worker_service.set_worker_active(i, True),
                                              "Worker reactivated.")).pack(side="left")
        self.refresh()

    def on_add(self):
        try:
            worker_service.add_worker(self.name_var.get(), self.trade_var.get(), self.contact_var.get())
            self.name_var.set("")
            self.contact_var.set("")
            self.refresh()
            messagebox.showinfo("Success", "Worker added.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Worker", "add_worker_ui", e)

    def _act(self, action, done_message):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Select a worker first.")
            return
        try:
            action(self.tree.item(selected[0])["values"][0])
            self.refresh()
            messagebox.showinfo("Success", done_message)
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Worker", "worker_action_ui", e)

    def refresh(self):
        keep_selection(self.tree, self._rebuild)

    def _rebuild(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for w in worker_service.get_workers():
            self.tree.insert("", "end", values=(
                w["worker_id"], w["name"], w["trade"], w["contact_number"], w["status"], w["today"],
                w["open_jobs"], w["done_jobs"]),
                tags=(status_tag(w["status"] if w["status"] == "Inactive" else w["today"]),))
