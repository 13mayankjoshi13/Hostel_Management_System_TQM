"""
Central visual theme — v4 (Batch 6).

Design direction: clean, neutral, restrained. One accent color used
sparingly (primary buttons, active nav, links). Flat surfaces, thin
1px borders, no colored accent stripes, no shadows, no gradients, no
pill-shaped buttons, modest type scale. Sidebar navigation (persistent,
plain-text) replaces Batch 5's splash-to-hub-tile model — a sidebar is
the more practical pattern for a tool used many times a day.
"""
import tkinter as tk
from tkinter import ttk, font as tkfont

COLORS = {
    "background": "#FAFAFA",
    "surface": "#FFFFFF",
    "sidebar_bg": "#F7F7F8",
    "border": "#E4E4E7",
    "border_strong": "#D4D4D8",

    "text_primary": "#18181B",
    "text_secondary": "#52525B",
    "text_tertiary": "#A1A1AA",

    "accent": "#3457D5",
    "accent_hover": "#2A44AC",
    "accent_soft": "#EEF1FD",

    "success": "#15803D",
    "success_soft": "#F0FDF4",
    "danger": "#B91C1C",
    "danger_soft": "#FEF2F2",
    "warning": "#B45309",
    "warning_soft": "#FFFBEB",
    "info": "#1D4ED8",

    # compatibility aliases used by existing screen files
    "card_bg": "#FFFFFF",
    "header_bg": "#FAFAFA",
    "text_dark": "#18181B",
    "text_muted": "#52525B",
}

STATUS_FG = {
    "Open": "#B45309",
    "Assigned": "#1D4ED8",
    "Resolved": "#15803D",
    "Active": "#15803D",
    "Released": "#71717A",
}


def get_fonts():
    return {
        "brand": tkfont.Font(family="Segoe UI", size=12, weight="bold"),
        "nav": tkfont.Font(family="Segoe UI", size=10),
        "nav_active": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "splash_title": tkfont.Font(family="Segoe UI", size=15, weight="bold"),
        "splash_tagline": tkfont.Font(family="Segoe UI", size=9),
        "header": tkfont.Font(family="Segoe UI", size=14, weight="bold"),
        "subheader": tkfont.Font(family="Segoe UI", size=9),
        "section_title": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "label": tkfont.Font(family="Segoe UI", size=9),
        "body": tkfont.Font(family="Segoe UI", size=10),
        "body_bold": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "table": tkfont.Font(family="Segoe UI", size=9),
        "table_heading": tkfont.Font(family="Segoe UI", size=9, weight="bold"),
        "stat_value": tkfont.Font(family="Segoe UI", size=19, weight="bold"),
        "stat_label": tkfont.Font(family="Segoe UI", size=9),
    }


def apply_theme(root) -> dict:
    root.configure(bg=COLORS["background"])
    fonts = get_fonts()

    style = ttk.Style(root)
    style.theme_use("alt")

    style.configure("TFrame", background=COLORS["background"])
    style.configure("FormLabel.TLabel", background=COLORS["surface"],
                     foreground=COLORS["text_secondary"], font=fonts["label"])

    style.configure("TEntry", fieldbackground=COLORS["surface"], foreground=COLORS["text_primary"],
                     bordercolor=COLORS["border_strong"], lightcolor=COLORS["border_strong"],
                     darkcolor=COLORS["border_strong"], insertcolor=COLORS["text_primary"],
                     padding=5, relief="solid", borderwidth=1)
    style.configure("TCombobox", fieldbackground=COLORS["surface"], foreground=COLORS["text_primary"],
                     bordercolor=COLORS["border_strong"], arrowcolor=COLORS["text_secondary"], padding=5)
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface"])])
    root.option_add("*TCombobox*Listbox.background", COLORS["surface"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text_primary"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent_soft"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["text_primary"])

    style.configure("Primary.TButton", background=COLORS["accent"], foreground="#FFFFFF",
                     font=fonts["body"], padding=(12, 6), borderwidth=0, relief="flat")
    style.map("Primary.TButton", background=[("active", COLORS["accent_hover"]),
                                                ("disabled", COLORS["border_strong"])])

    style.configure("Secondary.TButton", background=COLORS["surface"], foreground=COLORS["text_primary"],
                     font=fonts["body"], padding=(11, 5), borderwidth=1, relief="solid")
    style.map("Secondary.TButton", background=[("active", COLORS["background"])])

    style.configure("Danger.TButton", background=COLORS["surface"], foreground=COLORS["danger"],
                     font=fonts["body"], padding=(11, 5), borderwidth=1, relief="solid")
    style.map("Danger.TButton", background=[("active", COLORS["danger_soft"])])

    # NOTE: this Tk build renders Treeview row text in a stray blue
    # instead of the configured color whenever the BUILT-IN "Treeview"
    # style name is reconfigured (reproducible even with foreground
    # omitted entirely, across every bundled theme). Using a distinct,
    # app-owned style name sidesteps it, so every Treeview in the app is
    # created with style="App.Treeview" (see build_table below) rather
    # than relying on the default style name.
    style.configure("App.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                     foreground=COLORS["text_primary"], font=fonts["table"], rowheight=26, borderwidth=0)
    style.configure("App.Treeview.Heading", background=COLORS["sidebar_bg"], foreground=COLORS["text_secondary"],
                     font=fonts["table_heading"], borderwidth=0, relief="flat")
    style.map("App.Treeview", background=[("selected", COLORS["accent_soft"])],
              foreground=[("selected", COLORS["text_primary"]), ("!selected", COLORS["text_primary"])])

    style.configure("Vertical.TScrollbar", background=COLORS["background"], troughcolor=COLORS["background"])

    return fonts


def section_header(parent, title: str, subtitle: str, fonts: dict):
    """Plain page header: title + muted subtitle + thin divider. No box."""
    wrapper = tk.Frame(parent, bg=COLORS["background"])
    wrapper.pack(fill="x", padx=28, pady=(22, 16))
    tk.Label(wrapper, text=title, bg=COLORS["background"], fg=COLORS["text_primary"],
              font=fonts["header"]).pack(anchor="w")
    if subtitle:
        tk.Label(wrapper, text=subtitle, bg=COLORS["background"], fg=COLORS["text_secondary"],
                  font=fonts["subheader"]).pack(anchor="w", pady=(2, 0))
    tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x")


def form_row(parent, fonts, row_index: int, label_text: str, widget) -> None:
    """One label+field row inside an un-boxed form grid."""
    tk.Label(parent, text=label_text, bg=COLORS["background"], fg=COLORS["text_secondary"],
              font=fonts["label"]).grid(row=row_index, column=0, sticky="w", pady=7, padx=(0, 16))
    widget.grid(row=row_index, column=1, sticky="ew", pady=7)


def build_panel(parent, title: str, fonts: dict) -> tk.Frame:
    """
    A plain bordered panel used for data tables — thin 1px border, small
    title row with a bottom divider. No accent stripe, no shadow.
    Returns the inner content frame.
    """
    panel = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1,
                       highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    panel.pack(fill="both", expand=True)

    title_row = tk.Frame(panel, bg=COLORS["surface"])
    title_row.pack(fill="x", padx=18, pady=(12, 10))
    tk.Label(title_row, text=title, bg=COLORS["surface"], fg=COLORS["text_primary"],
              font=fonts["section_title"]).pack(anchor="w")
    tk.Frame(panel, bg=COLORS["border"], height=1).pack(fill="x")

    content = tk.Frame(panel, bg=COLORS["surface"])
    content.pack(fill="both", expand=True, padx=18, pady=14)
    return content


def build_stat_row(parent, stats, fonts: dict) -> tk.Frame:
    """
    A horizontal strip of label/value pairs separated by thin vertical
    dividers — used for Dashboard KPIs instead of a grid of colored cards.
    `stats` is a list of (label, value) tuples.
    """
    row = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1,
                     highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])
    row.pack(fill="x")

    for i, (label, value) in enumerate(stats):
        cell = tk.Frame(row, bg=COLORS["surface"])
        cell.pack(side="left", fill="both", expand=True, padx=20, pady=14)
        tk.Label(cell, text=value, bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["stat_value"]).pack(anchor="w")
        tk.Label(cell, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["stat_label"]).pack(anchor="w", pady=(2, 0))
        if i < len(stats) - 1:
            tk.Frame(row, bg=COLORS["border"], width=1).pack(side="left", fill="y", pady=14)
    return row


def build_table(parent, columns, headings, widths, height=10) -> ttk.Treeview:
    """Create a Treeview with the app's style name and column setup in one call."""
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=height,
                          style="App.Treeview")
    for col, label, width in zip(columns, headings, widths):
        tree.heading(col, text=label)
        tree.column(col, width=width, anchor="w")
    return tree


def style_treeview_status_tags(tree: ttk.Treeview):
    """
    ttk's 'clam' theme does not reliably honor the plain Treeview
    'foreground' style option for row text on every platform/build — it
    can fall back to a theme default (a blue tone) unless each row has
    an explicit tag. So every row gets a tag: either a semantic status
    color, or 'default' for plain near-black text.
    """
    tree.tag_configure("default", foreground=COLORS["text_primary"])
    for status, color in STATUS_FG.items():
        tree.tag_configure(f"status_{status.lower()}", foreground=color)


def status_tag(status: str) -> str:
    return f"status_{status.lower()}"


def bind_hover(widget, normal_bg: str, hover_bg: str):
    """Subtle background-swap hover for plain tk widgets (sidebar items, links)."""
    widget.bind("<Enter>", lambda e: widget.configure(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.configure(bg=normal_bg))
