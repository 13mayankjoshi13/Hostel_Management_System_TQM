"""
Central visual theme for the whole application.

Every screen imports COLORS / FONTS and calls the small helper widgets
below (build_card, styled Treeview setup) instead of hand-rolling colors,
so the whole app looks consistent and a single file controls the look.

Kept as plain Tkinter/ttk (no external dependency) since the project
direction is Python + SQLite + Tkinter.
"""
import tkinter as tk
from tkinter import ttk, font as tkfont

COLORS = {
    "primary": "#4F46E5",        # indigo — primary actions, active nav
    "primary_dark": "#3730A3",
    "primary_light": "#EEF2FF",
    "success": "#059669",
    "success_light": "#ECFDF5",
    "danger": "#DC2626",
    "danger_light": "#FEF2F2",
    "warning": "#D97706",
    "warning_light": "#FFFBEB",
    "sidebar_bg": "#1E1B4B",     # deep indigo/navy
    "sidebar_hover": "#312E81",
    "sidebar_text": "#C7D2FE",
    "sidebar_text_active": "#FFFFFF",
    "background": "#F3F4F6",
    "card_bg": "#FFFFFF",
    "border": "#E5E7EB",
    "text_dark": "#111827",
    "text_muted": "#6B7280",
    "header_bg": "#FFFFFF",
}

STATUS_COLORS = {
    "Open": ("#D97706", "#FFFBEB"),
    "Assigned": ("#2563EB", "#EFF6FF"),
    "Resolved": ("#059669", "#ECFDF5"),
    "Active": ("#059669", "#ECFDF5"),
    "Released": ("#6B7280", "#F3F4F6"),
}


def get_fonts():
    """Must be called AFTER a Tk root exists (font.Font needs one)."""
    return {
        "app_title": tkfont.Font(family="Segoe UI", size=15, weight="bold"),
        "nav": tkfont.Font(family="Segoe UI", size=11),
        "nav_active": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
        "header": tkfont.Font(family="Segoe UI", size=16, weight="bold"),
        "subheader": tkfont.Font(family="Segoe UI", size=10),
        "card_title": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
        "body": tkfont.Font(family="Segoe UI", size=10),
        "body_bold": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "table": tkfont.Font(family="Segoe UI", size=10),
        "table_heading": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
    }


def apply_theme(root) -> dict:
    """
    Configure ttk styles for the whole app. Returns the FONTS dict so
    callers don't need a second call to get_fonts().
    """
    root.configure(bg=COLORS["background"])
    fonts = get_fonts()

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["card_bg"])
    style.configure("Header.TFrame", background=COLORS["header_bg"])

    style.configure(
        "CardTitle.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_dark"],
        font=fonts["card_title"],
    )
    style.configure(
        "ScreenHeader.TLabel",
        background=COLORS["header_bg"],
        foreground=COLORS["text_dark"],
        font=fonts["header"],
    )
    style.configure(
        "ScreenSubheader.TLabel",
        background=COLORS["header_bg"],
        foreground=COLORS["text_muted"],
        font=fonts["subheader"],
    )
    style.configure(
        "FormLabel.TLabel",
        background=COLORS["card_bg"],
        foreground=COLORS["text_dark"],
        font=fonts["body"],
    )

    style.configure(
        "TEntry",
        fieldbackground="#FFFFFF",
        bordercolor=COLORS["border"],
        padding=6,
    )
    style.configure(
        "TCombobox",
        fieldbackground="#FFFFFF",
        padding=6,
    )

    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="#FFFFFF",
        font=fonts["body_bold"],
        padding=(14, 8),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_dark"]), ("disabled", COLORS["border"])],
    )

    style.configure(
        "Secondary.TButton",
        background=COLORS["card_bg"],
        foreground=COLORS["primary"],
        font=fonts["body"],
        padding=(12, 7),
        borderwidth=1,
        relief="solid",
    )
    style.map("Secondary.TButton", background=[("active", COLORS["primary_light"])])

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="#FFFFFF",
        font=fonts["body_bold"],
        padding=(12, 7),
        borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", "#B91C1C")])

    style.configure(
        "Treeview",
        background=COLORS["card_bg"],
        fieldbackground=COLORS["card_bg"],
        foreground=COLORS["text_dark"],
        font=fonts["table"],
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["primary_light"],
        foreground=COLORS["primary_dark"],
        font=fonts["table_heading"],
        borderwidth=0,
        relief="flat",
    )
    style.map("Treeview", background=[("selected", COLORS["primary"])],
              foreground=[("selected", "#FFFFFF")])

    style.configure("Vertical.TScrollbar", background=COLORS["background"])

    return fonts


def build_card(parent, title: str, fonts: dict) -> ttk.Frame:
    """
    A padded white 'card' with a title strip on top — the app's standard
    container for forms and tables, used in place of a plain
    ttk.LabelFrame for a less boxy, more modern look.
    Returns the INNER content frame; put widgets inside that.
    """
    outer = tk.Frame(parent, bg=COLORS["border"], bd=0)
    outer.pack(fill="both", expand=False, padx=0, pady=(0, 12))

    card = tk.Frame(outer, bg=COLORS["card_bg"], bd=0)
    card.pack(fill="both", expand=True, padx=1, pady=1)

    title_row = tk.Frame(card, bg=COLORS["card_bg"])
    title_row.pack(fill="x", padx=16, pady=(12, 4))
    tk.Label(
        title_row, text=title, bg=COLORS["card_bg"], fg=COLORS["text_dark"],
        font=fonts["card_title"],
    ).pack(anchor="w")

    content = tk.Frame(card, bg=COLORS["card_bg"])
    content.pack(fill="both", expand=True, padx=16, pady=(4, 16))
    return content


def status_badge(parent, status: str, fonts: dict) -> tk.Label:
    fg, bg = STATUS_COLORS.get(status, (COLORS["text_muted"], COLORS["background"]))
    return tk.Label(
        parent, text=f"  {status}  ", bg=bg, fg=fg,
        font=fonts["body_bold"], bd=0,
    )


def style_treeview_stripes(tree: ttk.Treeview):
    """Call once after creating a Treeview to enable alternating row colors."""
    tree.tag_configure("oddrow", background=COLORS["card_bg"])
    tree.tag_configure("evenrow", background="#F9FAFB")


def stripe_tag(index: int) -> str:
    return "evenrow" if index % 2 == 0 else "oddrow"
