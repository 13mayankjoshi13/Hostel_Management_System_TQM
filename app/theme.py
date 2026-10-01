"""
Central visual theme for the whole application — v3 (Batch 5 redesign).

This is a full layout-and-color departure from both earlier looks:
  - Batch 3: light, indigo palette, LEFT SIDEBAR with 5 nav items.
  - Batch 4: light, teal palette, TOP NAVBAR with 5 nav pills.
  - Batch 5 (this one): DARK theme, electric-cyan accent, HUB-AND-SPOKE
    navigation — a splash screen on launch, a Dashboard "hub" with big
    clickable module tiles, and a breadcrumb + Home button inside every
    other screen to get back. There is no persistent multi-item nav bar
    at all anymore.

Every screen still imports COLORS / FONTS and the helper widgets below
instead of hand-rolling colors, so the whole app stays consistent and
this one file controls the look.
"""
import tkinter as tk
from tkinter import ttk, font as tkfont

COLORS = {
    # Core dark surfaces
    "background": "#0B1120",       # app background — near-black navy
    "surface": "#131C2E",          # raised surface (used as card_bg)
    "surface_alt": "#0F172A",      # input fields, popdown lists
    "border": "#1E293B",

    # Text
    "text_light": "#E2E8F0",
    "text_dark": "#E2E8F0",         # kept name for compatibility with existing screens; means "primary text" now
    "text_muted": "#94A3B8",

    # Brand / accent — electric cyan (replaces indigo then teal)
    "primary": "#22D3EE",
    "primary_dark": "#06B6D4",
    "primary_on": "#04222B",        # text color to use ON TOP of a primary-colored background

    "accent_violet": "#A78BFA",
    "accent_amber": "#FBBF24",
    "accent_blue": "#60A5FA",

    "success": "#34D399",
    "success_soft": "#052E22",
    "danger": "#FB7185",
    "danger_soft": "#3F0B17",
    "warning": "#FBBF24",
    "warning_soft": "#3A2A05",

    "topbar_bg": "#070B14",
    "card_bg": "#131C2E",           # alias, matches "surface"
    "header_bg": "#0B1120",         # screen header strip — same as app background now (no white strip)
}

STATUS_COLORS = {
    "Open": ("#FBBF24", "#3A2A05"),
    "Assigned": ("#60A5FA", "#0B2545"),
    "Resolved": ("#34D399", "#052E22"),
    "Active": ("#34D399", "#052E22"),
    "Released": ("#94A3B8", "#1E293B"),
}


def get_fonts():
    """Must be called AFTER a Tk root exists (font.Font needs one)."""
    return {
        "splash_title": tkfont.Font(family="Segoe UI", size=20, weight="bold"),
        "splash_tagline": tkfont.Font(family="Segoe UI", size=10),
        "brand": tkfont.Font(family="Segoe UI", size=13, weight="bold"),
        "header": tkfont.Font(family="Segoe UI", size=18, weight="bold"),
        "subheader": tkfont.Font(family="Segoe UI", size=10),
        "card_title": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
        "body": tkfont.Font(family="Segoe UI", size=10),
        "body_bold": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "table": tkfont.Font(family="Segoe UI", size=10),
        "table_heading": tkfont.Font(family="Segoe UI", size=9, weight="bold"),
        "stat_value": tkfont.Font(family="Segoe UI", size=26, weight="bold"),
        "stat_label": tkfont.Font(family="Segoe UI", size=10),
        "tile_icon": tkfont.Font(family="Segoe UI", size=22),
        "tile_title": tkfont.Font(family="Segoe UI", size=13, weight="bold"),
        "tile_subtitle": tkfont.Font(family="Segoe UI", size=9),
    }


def apply_theme(root) -> dict:
    """Configure ttk styles (dark) for the whole app. Returns the FONTS dict."""
    root.configure(bg=COLORS["background"])
    fonts = get_fonts()

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["surface"])

    style.configure("CardTitle.TLabel", background=COLORS["surface"],
                     foreground=COLORS["text_light"], font=fonts["card_title"])
    style.configure("ScreenHeader.TLabel", background=COLORS["header_bg"],
                     foreground=COLORS["text_light"], font=fonts["header"])
    style.configure("ScreenSubheader.TLabel", background=COLORS["header_bg"],
                     foreground=COLORS["text_muted"], font=fonts["subheader"])
    style.configure("FormLabel.TLabel", background=COLORS["surface"],
                     foreground=COLORS["text_light"], font=fonts["body"])

    style.configure("TEntry", fieldbackground=COLORS["surface_alt"],
                     foreground=COLORS["text_light"], insertcolor=COLORS["text_light"],
                     bordercolor=COLORS["border"], padding=6)
    style.configure("TCombobox", fieldbackground=COLORS["surface_alt"],
                     background=COLORS["surface_alt"], foreground=COLORS["text_light"],
                     arrowcolor=COLORS["text_light"], padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface_alt"])],
              foreground=[("readonly", COLORS["text_light"])])
    root.option_add("*TCombobox*Listbox.background", COLORS["surface_alt"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text_light"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["primary"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["primary_on"])

    style.configure("Primary.TButton", background=COLORS["primary"], foreground=COLORS["primary_on"],
                     font=fonts["body_bold"], padding=(14, 9), borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_dark"]), ("disabled", COLORS["border"])])

    style.configure("Secondary.TButton", background=COLORS["surface"], foreground=COLORS["primary"],
                     font=fonts["body"], padding=(12, 8), borderwidth=1, relief="solid")
    style.map("Secondary.TButton", background=[("active", COLORS["surface_alt"])])

    style.configure("Danger.TButton", background=COLORS["danger"], foreground="#2B0510",
                     font=fonts["body_bold"], padding=(12, 8), borderwidth=0)
    style.map("Danger.TButton", background=[("active", "#F43F5E")])

    style.configure("Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                     foreground=COLORS["text_light"], font=fonts["table"], rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", background=COLORS["surface_alt"], foreground=COLORS["primary"],
                     font=fonts["table_heading"], borderwidth=0, relief="flat")
    style.map("Treeview", background=[("selected", COLORS["primary"])],
              foreground=[("selected", COLORS["primary_on"])])

    style.configure("Vertical.TScrollbar", background=COLORS["background"])

    return fonts


def build_card(parent, title: str, fonts: dict, accent: str = None) -> tk.Frame:
    """
    A dark 'elevated' card: thin border + a colored top accent stripe.
    Returns the INNER content frame; put widgets inside that.
    """
    accent = accent or COLORS["primary"]

    card = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1,
                     highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    card.pack(fill="both", expand=False, pady=(0, 16))

    tk.Frame(card, bg=accent, height=4).pack(fill="x")

    title_row = tk.Frame(card, bg=COLORS["surface"])
    title_row.pack(fill="x", padx=20, pady=(14, 4))
    tk.Label(title_row, text=title, bg=COLORS["surface"], fg=COLORS["text_light"],
              font=fonts["card_title"]).pack(anchor="w")

    content = tk.Frame(card, bg=COLORS["surface"])
    content.pack(fill="both", expand=True, padx=20, pady=(4, 20))
    return content


def build_stat_card(parent, label: str, value: str, accent: str, fonts: dict) -> tk.Frame:
    """A compact dashboard stat tile: big number, label, colored accent stripe."""
    card = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1,
                     highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    tk.Frame(card, bg=accent, height=4).pack(fill="x")

    inner = tk.Frame(card, bg=COLORS["surface"])
    inner.pack(fill="both", expand=True, padx=18, pady=16)
    tk.Label(inner, text=value, bg=COLORS["surface"], fg=COLORS["text_light"],
              font=fonts["stat_value"]).pack(anchor="w")
    tk.Label(inner, text=label, bg=COLORS["surface"], fg=COLORS["text_muted"],
              font=fonts["stat_label"]).pack(anchor="w", pady=(2, 0))
    return card


def build_module_tile(parent, icon: str, title: str, subtitle: str, accent: str,
                        command, fonts: dict) -> tk.Frame:
    """
    A big clickable hub tile used on the Dashboard to navigate into a
    module (Students / Rooms / Room Allocation / Complaints). Replaces
    the persistent nav bar/sidebar used in earlier batches — navigation
    now happens by clicking into a module from the hub, plus a Home
    breadcrumb inside each module screen to come back.
    """
    tile = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1,
                      highlightbackground=COLORS["border"], highlightcolor=COLORS["border"],
                      cursor="hand2")
    tk.Frame(tile, bg=accent, height=4).pack(fill="x")

    inner = tk.Frame(tile, bg=COLORS["surface"])
    inner.pack(fill="both", expand=True, padx=20, pady=18)

    tk.Label(inner, text=icon, bg=COLORS["surface"], fg=accent,
              font=fonts["tile_icon"]).pack(anchor="w")
    tk.Label(inner, text=title, bg=COLORS["surface"], fg=COLORS["text_light"],
              font=fonts["tile_title"]).pack(anchor="w", pady=(8, 2))
    tk.Label(inner, text=subtitle, bg=COLORS["surface"], fg=COLORS["text_muted"],
              font=fonts["tile_subtitle"], wraplength=200, justify="left").pack(anchor="w")

    def _bind_click(widget):
        widget.bind("<Button-1>", lambda e: command())
        for child in widget.winfo_children():
            _bind_click(child)

    def _on_enter(_e):
        tile.configure(highlightbackground=accent)

    def _on_leave(_e):
        tile.configure(highlightbackground=COLORS["border"])

    _bind_click(tile)
    tile.bind("<Enter>", _on_enter)
    tile.bind("<Leave>", _on_leave)

    return tile


def build_breadcrumb(parent, screen_name: str, go_home, fonts: dict):
    """
    Small 'Home > Screen' row placed at the top of every non-Dashboard
    screen. Clicking 'Home' calls go_home() — this plus the Dashboard's
    module tiles is the entire navigation system in this layout (no
    persistent nav bar/sidebar).
    """
    row = tk.Frame(parent, bg=COLORS["header_bg"])
    row.pack(fill="x", padx=24, pady=(14, 0))

    home_lbl = tk.Label(row, text="🏠 Dashboard", bg=COLORS["header_bg"], fg=COLORS["primary"],
                          font=fonts["body_bold"], cursor="hand2")
    home_lbl.pack(side="left")
    home_lbl.bind("<Button-1>", lambda e: go_home())

    tk.Label(row, text="   ›   ", bg=COLORS["header_bg"], fg=COLORS["text_muted"],
              font=fonts["body"]).pack(side="left")
    tk.Label(row, text=screen_name, bg=COLORS["header_bg"], fg=COLORS["text_muted"],
              font=fonts["body"]).pack(side="left")


def status_badge(parent, status: str, fonts: dict) -> tk.Label:
    fg, bg = STATUS_COLORS.get(status, (COLORS["text_muted"], COLORS["surface_alt"]))
    return tk.Label(parent, text=f"  {status}  ", bg=bg, fg=fg, font=fonts["body_bold"], bd=0)


def style_treeview_stripes(tree: ttk.Treeview):
    """Call once after creating a Treeview to enable alternating row colors."""
    tree.tag_configure("oddrow", background=COLORS["surface"])
    tree.tag_configure("evenrow", background=COLORS["surface_alt"])


def stripe_tag(index: int) -> str:
    return "evenrow" if index % 2 == 0 else "oddrow"
