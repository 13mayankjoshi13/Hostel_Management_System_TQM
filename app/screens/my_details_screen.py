"""Student portal: view and edit your own details."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import student_portal_service
from app.utils.validation import ValidationError
from app.utils.exception_handler import handle_unexpected_error
from app.theme import COLORS, section_header, form_row, form_card, button_row


class MyDetailsScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Details", "Keep your name and contact number up to date.", fonts)
        holder = tk.Frame(self, bg=COLORS["background"])
        holder.pack(fill="x", padx=28, pady=(18, 0))
        wrapper = form_card(holder, "Your details", fonts)

        self.name_var = tk.StringVar()
        self.reg_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        form_row(wrapper, fonts, 0, "Name", ttk.Entry(wrapper, textvariable=self.name_var))
        form_row(wrapper, fonts, 1, "Registration No.", ttk.Entry(wrapper, textvariable=self.reg_var, state="readonly"))
        form_row(wrapper, fonts, 2, "Contact No.", ttk.Entry(wrapper, textvariable=self.contact_var))
        buttons = button_row(wrapper, 3)
        ttk.Button(buttons, text="Save Changes", style="Primary.TButton", command=self.on_save).pack(side="left")
        tk.Label(wrapper, text="The registration number is set by the hostel office; ask them to change it.",
                  bg=wrapper.cget("bg"), fg=COLORS["text_tertiary"], font=fonts["label"]).grid(
            row=4, column=1, sticky="w", pady=(8, 0))

    def on_save(self):
        try:
            student_portal_service.update_my_details(self.name_var.get(), self.contact_var.get())
            self.refresh()
            messagebox.showinfo("Success", "Your details were updated.")
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            handle_unexpected_error("Portal", "update_my_details_ui", e)

    def refresh(self):
        details = student_portal_service.my_details()
        self.name_var.set(details.get("name", ""))
        self.reg_var.set(details.get("registration_number", ""))
        self.contact_var.set(details.get("contact_number", ""))
