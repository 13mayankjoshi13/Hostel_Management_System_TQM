"""
Central visual theme for the whole application — v2 (Batch 4 redesign).

This is a deliberate, ground-up visual change from the Batch 3 look:
  - Batch 3: indigo palette, dark LEFT SIDEBAR navigation, bordered boxy cards.
  - Batch 4: teal/slate palette, dark TOP NAVBAR navigation, cards with a
    colored accent stripe and a soft single-pixel border instead of a
    heavy box outline, plus a new Dashboard landing screen.

Every screen still imports COLORS / FONTS and the helper widgets below
instead of hand-rolling colors, so the whole app stays consistent and
this one file controls the look.
"""
import tkinter as tk
from tkinter import ttk, font as tkfont

COLORS = {
    "primary": "#0D9488",         # teal-600 — primary actions, active nav
    "primary_dark": "#0F766E",
    "primary_light": "#F0FDFA",
    "accent_blue": "#2563EB",
    "accent_blue_light": "#EFF6FF",
    "accent_amber": "#D97706",
    "accent_amber_light": "#FFFBEB",
    "accent_rose": "#E11D48",
    "accent_rose_light": "#FFF1F2",

    "success": "#16A34A",
    "success_light": "#F0FDF4",
    "danger": "#E11D48",
    "danger_light": "#FFF1F2",
    "warning": "#D97706",
    "warning_light": "#FFFBEB",

    "navbar_bg": "#0F172A",        # slate-900 — top navigation bar
    "navbar_pill_active": "#0D9488",
    "navbar_text": "#94A3B8",
    "navbar_text_active": "#FFFFFF",

    "background": "#F8FAFC",       # slate-50
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text_dark": "#0F172A",
    "text_muted": "#64748B",
    "header_bg": "#FFFFFF",
}

STATUS_COLORS = {
    "Open": ("#D97706", "#FFFBEB"),
    "Assigned": ("#2563EB", "#EFF6FF"),
    "Resolved": ("#16A34A", "#F0FDF4"),
    "Active": ("#16A34A", "#F0FDF4"),
    "Released": ("#64748B", "#F1F5F9"),
}


def get_fonts():
    """Must be called AFTER a Tk root exists (font.Font needs one)."""
    return {
        "brand": tkfont.Font(family="Segoe UI", size=14, weight="bold"),
        "nav": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "header": tkfont.Font(family="Segoe UI", size=17, weight="bold"),
        "subheader": tkfont.Font(family="Segoe UI", size=10),
        "card_title": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
        "body": tkfont.Font(family="Segoe UI", size=10),
        "body_bold": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "table": tkfont.Font(family="Segoe UI", size=10),
        "table_heading": tkfont.Font(family="Segoe UI", size=9, weight="bold"),
        "stat_value": tkfont.Font(family="Segoe UI", size=26, weight="bold"),
        "stat_label": tkfont.Font(family="Segoe UI", size=10),
    }


def apply_theme(root) -> dict:
    """Configure ttk styles for the whole app. Returns the FONTS dict."""
    root.configure(bg=COLORS["background"])
    fonts = get_fonts()

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["card_bg"])
    style.configure("Header.TFrame", background=COLORS["header_bg"])

    style.configure(
        "CardTitle.TLabel", background=COLORS["card_bg"],
        foreground=COLORS["text_dark"], font=fonts["card_title"],
    )
    style.configure(
        "ScreenHeader.TLabel", background=COLORS["header_bg"],
        foreground=COLORS["text_dark"], font=fonts["header"],
    )
    style.configure(
        "ScreenSubheader.TLabel", background=COLORS["header_bg"],
        foreground=COLORS["text_muted"], font=fonts["subheader"],
    )
    style.configure(
        "FormLabel.TLabel", background=COLORS["card_bg"],
        foreground=COLORS["text_dark"], font=fonts["body"],
    )

    style.configure("TEntry", fieldbackground="#FFFFFF",
                     bordercolor=COLORS["border"], padding=6)
    style.configure("TCombobox", fieldbackground="#FFFFFF", padding=6)

    style.configure(
        "Primary.TButton", background=COLORS["primary"], foreground="#FFFFFF",
        font=fonts["body_bold"], padding=(14, 9), borderwidth=0,
    )
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_dark"]), ("disabled", COLORS["border"])])

    style.configure(
        "Secondary.TButton", background=COLORS["card_bg"], foreground=COLORS["primary"],
        font=fonts["body"], padding=(12, 8), borderwidth=1, relief="solid",
    )
    style.map("Secondary.TButton", background=[("active", COLORS["primary_light"])])

    style.configure(
        "Danger.TButton", background=COLORS["danger"], foreground="#FFFFFF",
        font=fonts["body_bold"], padding=(12, 8), borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", "#BE123C")])

    style.configure(
        "Treeview", background=COLORS["card_bg"], fieldbackground=COLORS["card_bg"],
        foreground=COLORS["text_dark"], font=fonts["table"], rowheight=30, borderwidth=0,
    )
    style.configure(
        "Treeview.Heading", background=COLORS["primary_light"], foreground=COLORS["primary_dark"],
        font=fonts["table_heading"], borderwidth=0, relief="flat",
    )
    style.map("Treeview", background=[("selected", COLORS["primary"])],
              foreground=[("selected", "#FFFFFF")])

    style.configure("Vertical.TScrollbar", background=COLORS["background"])

    return fonts


def build_card(parent, title: str, fonts: dict, accent: str = None) -> tk.Frame:
    """
    A white 'elevated' card: thin border + a colored top accent stripe,
    used in place of the Batch 3 boxy LabelFrame-style container.
    Returns the INNER content frame; put widgets inside that.
    """
    accent = accent or COLORS["primary"]

    card = tk.Frame(parent, bg=COLORS["card_bg"], highlightthickness=1,
                     highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    card.pack(fill="both", expand=False, pady=(0, 16))

    tk.Frame(card, bg=accent, height=4).pack(fill="x")

    title_row = tk.Frame(card, bg=COLORS["card_bg"])
    title_row.pack(fill="x", padx=20, pady=(14, 4))
    tk.Label(title_row, text=title, bg=COLORS["card_bg"], fg=COLORS["text_dark"],
              font=fonts["card_title"]).pack(anchor="w")

    content = tk.Frame(card, bg=COLORS["card_bg"])
    content.pack(fill="both", expand=True, padx=20, pady=(4, 20))
    return content


def build_stat_card(parent, label: str, value: str, accent: str, fonts: dict) -> tk.Frame:
    """A compact dashboard stat tile: big number, label, colored accent stripe."""
    card = tk.Frame(parent, bg=COLORS["card_bg"], highlightthickness=1,
                     highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    tk.Frame(card, bg=accent, height=4).pack(fill="x")

    inner = tk.Frame(card, bg=COLORS["card_bg"])
    inner.pack(fill="both", expand=True, padx=18, pady=16)
    tk.Label(inner, text=value, bg=COLORS["card_bg"], fg=COLORS["text_dark"],
              font=fonts["stat_value"]).pack(anchor="w")
    tk.Label(inner, text=label, bg=COLORS["card_bg"], fg=COLORS["text_muted"],
              font=fonts["stat_label"]).pack(anchor="w", pady=(2, 0))
    return card


def status_badge(parent, status: str, fonts: dict) -> tk.Label:
    fg, bg = STATUS_COLORS.get(status, (COLORS["text_muted"], COLORS["background"]))
    return tk.Label(parent, text=f"  {status}  ", bg=bg, fg=fg, font=fonts["body_bold"], bd=0)


def style_treeview_stripes(tree: ttk.Treeview):
    """Call once after creating a Treeview to enable alternating row colors."""
    tree.tag_configure("oddrow", background=COLORS["card_bg"])
    tree.tag_configure("evenrow", background="#F8FAFC")


def stripe_tag(index: int) -> str:
    return "evenrow" if index % 2 == 0 else "oddrow"
