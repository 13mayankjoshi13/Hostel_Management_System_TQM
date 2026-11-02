"""Student portal: notices addressed to you, your hostel, or everyone."""
import tkinter as tk

from app.services import notice_service
from app.theme import COLORS, section_header, build_panel


class MyNoticesScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "My Notices", "Announcements from the hostel office.", fonts)
        from app.theme import ScrollFrame
        self.sf = ScrollFrame(self)
        self.sf.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.content = self.sf.inner

    def refresh(self):
        for child in self.sf.inner.winfo_children():
            child.destroy()
        notices = notice_service.notices_for_student()
        if not notices:
            empty_box = tk.Frame(self.sf.inner, bg=COLORS["surface"], padx=24, pady=32,
                                 highlightthickness=1, highlightbackground=COLORS["border"])
            empty_box.pack(fill="x", pady=10)
            tk.Label(empty_box, text="No notices yet.", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=self.fonts["header"]).pack(anchor="w")
            tk.Label(empty_box, text="When the hostel staff or wardens post announcements, they will appear here.",
                     bg=COLORS["surface"], fg=COLORS["text_tertiary"], font=self.fonts["body"]).pack(anchor="w", pady=(4, 0))
            return

        from app.theme import Card, make_clickable, show_detail_dialog
        for n in notices:
            card = Card(self.sf.inner, fit=True, shadow=True)
            card.pack(fill="x", pady=(0, 12))
            body = card.body

            top_row = tk.Frame(body, bg=COLORS["surface"])
            top_row.pack(fill="x", pady=(0, 4))

            title_lbl = tk.Label(top_row, text=n["title"], bg=COLORS["surface"], fg=COLORS["text_primary"],
                                 font=self.fonts.get("heading", self.fonts["section_title"]))
            title_lbl.pack(side="left", anchor="w")

            aud = n.get("audience", "All")
            badge_bg = COLORS["accent_soft"] if aud == "Student" else COLORS["background"]
            badge_fg = COLORS["accent"] if aud == "Student" else COLORS["text_secondary"]
            badge_text = "Personal" if aud == "Student" else f"To: {aud}"
            badge = tk.Label(top_row, text=badge_text, bg=badge_bg, fg=badge_fg,
                             font=self.fonts["label"], padx=8, pady=2)
            badge.pack(side="right")

            meta_text = f"Posted by {n['created_by']}  •  {n['created_at']}"
            meta_lbl = tk.Label(body, text=meta_text, bg=COLORS["surface"],
                                fg=COLORS["text_tertiary"], font=self.fonts["label"])
            meta_lbl.pack(anchor="w", pady=(0, 6))

            desc_lbl = tk.Label(body, text=n["body"], bg=COLORS["surface"], fg=COLORS["text_secondary"],
                                font=self.fonts["body"], wraplength=700, justify="left")
            desc_lbl.pack(anchor="w", pady=(0, 8))

            def _show_notice(notice_data=n):
                show_detail_dialog(
                    title="Notice Details",
                    fields={
                        "Title": notice_data["title"],
                        "Audience": notice_data.get("audience", "All"),
                        "Posted By": notice_data["created_by"],
                        "Date": notice_data["created_at"],
                    },
                    full_text=notice_data["body"]
                )

            make_clickable(card, _show_notice)
            make_clickable(body, _show_notice)
            make_clickable(title_lbl, _show_notice)
            make_clickable(meta_lbl, _show_notice)
            make_clickable(desc_lbl, _show_notice)
            make_clickable(top_row, _show_notice)

