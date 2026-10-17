"""
Central visual theme — v5 (Batch 18).

Design direction: soft light-gray page, white rounded cards with a faint
shadow, one indigo accent plus a few colored icon tiles, icon sidebar,
top bar with clock and account chip. Cards and icons are drawn on Canvas
(no image files needed).
"""
import tkinter as tk
from tkinter import ttk, font as tkfont

FONT_FAMILY = "Segoe UI"

COLORS = {
    "background": "#F3F5FA",
    "surface": "#FFFFFF",
    "sidebar_bg": "#FFFFFF",
    "border": "#E7EAF2",
    "border_strong": "#D5DAE6",
    "shadow": "#E4E8F1",

    "text_primary": "#1E2235",
    "text_secondary": "#5B6275",
    "text_tertiary": "#9AA1B5",

    "accent": "#5B50E6",
    "accent_hover": "#4A3FD0",
    "accent_soft": "#EEECFD",

    "success": "#16A34A",
    "success_soft": "#E8F7EE",
    "danger": "#E5484D",
    "danger_soft": "#FDECEC",
    "warning": "#E58A00",
    "warning_soft": "#FFF3DF",
    "info": "#3B82F6",
    "info_soft": "#E8F1FE",
    "teal": "#14A38B",
    "teal_soft": "#E2F6F2",
    "pink": "#E5447A",
    "pink_soft": "#FCE8EF",
    "orange": "#F29A2E",
    "orange_soft": "#FEF1DE",

    "hero": "#2B2768",
    "hero_alt": "#3A3591",
    "hero_alt2": "#4A44B3",

    # compatibility aliases used by existing screen files
    "card_bg": "#FFFFFF",
    "header_bg": "#F3F5FA",
    "text_dark": "#1E2235",
    "text_muted": "#5B6275",
}

STATUS_FG = {
    "Open": "#E58A00",
    "Assigned": "#3B82F6",
    "Resolved": "#16A34A",
    "Active": "#16A34A",
    "Released": "#71717A",
    "In Progress": "#3B82F6",
    "Fixed": "#16A34A",
    "Closed": "#71717A",
    "On Leave": "#E58A00",
    "Returned": "#16A34A",
    "Pending": "#E58A00",
}


def get_fonts():
    return {
        "brand": tkfont.Font(family=FONT_FAMILY, size=12, weight="bold"),
        "nav": tkfont.Font(family=FONT_FAMILY, size=10),
        "nav_active": tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
        "splash_title": tkfont.Font(family=FONT_FAMILY, size=15, weight="bold"),
        "splash_tagline": tkfont.Font(family=FONT_FAMILY, size=9),
        "header": tkfont.Font(family=FONT_FAMILY, size=17, weight="bold"),
        "subheader": tkfont.Font(family=FONT_FAMILY, size=9),
        "section_title": tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
        "label": tkfont.Font(family=FONT_FAMILY, size=9),
        "body": tkfont.Font(family=FONT_FAMILY, size=10),
        "body_bold": tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
        "table": tkfont.Font(family=FONT_FAMILY, size=9),
        "table_heading": tkfont.Font(family=FONT_FAMILY, size=9, weight="bold"),
        "stat_value": tkfont.Font(family=FONT_FAMILY, size=19, weight="bold"),
        "kpi": tkfont.Font(family=FONT_FAMILY, size=22, weight="bold"),
        "hero": tkfont.Font(family=FONT_FAMILY, size=18, weight="bold"),
        "small": tkfont.Font(family=FONT_FAMILY, size=8),
        "small_bold": tkfont.Font(family=FONT_FAMILY, size=8, weight="bold"),
        "stat_label": tkfont.Font(family=FONT_FAMILY, size=9),
    }


def apply_theme(root) -> dict:
    root.configure(bg=COLORS["background"])
    fonts = get_fonts()

    style = ttk.Style(root)
    style.theme_use("alt")

    style.configure("TFrame", background=COLORS["background"])
    style.configure("TEntry", fieldbackground=COLORS["surface"], foreground=COLORS["text_primary"],
                     bordercolor=COLORS["border_strong"], lightcolor=COLORS["border_strong"],
                     darkcolor=COLORS["border_strong"], insertcolor=COLORS["text_primary"],
                     padding=6, relief="solid", borderwidth=1)
    style.map("TEntry", bordercolor=[("focus", COLORS["accent"])],
              lightcolor=[("focus", COLORS["accent"])], darkcolor=[("focus", COLORS["accent"])])
    style.configure("TCombobox", fieldbackground=COLORS["surface"], foreground=COLORS["text_primary"],
                     bordercolor=COLORS["border_strong"], arrowcolor=COLORS["text_secondary"], padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface"])])
    root.option_add("*TCombobox*Listbox.background", COLORS["surface"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text_primary"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent_soft"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["text_primary"])

    style.configure("Primary.TButton", background=COLORS["accent"], foreground="#FFFFFF",
                     font=fonts["body_bold"], padding=(16, 8), borderwidth=0, relief="flat")
    style.map("Primary.TButton", background=[("active", COLORS["accent_hover"]),
                                                ("disabled", COLORS["border_strong"])])

    style.configure("Secondary.TButton", background=COLORS["surface"], foreground=COLORS["text_primary"],
                     font=fonts["body"], padding=(14, 7), borderwidth=1, relief="solid",
                     bordercolor=COLORS["border_strong"])
    style.map("Secondary.TButton", background=[("active", COLORS["accent_soft"])])

    style.configure("Danger.TButton", background=COLORS["surface"], foreground=COLORS["danger"],
                     font=fonts["body"], padding=(14, 7), borderwidth=1, relief="solid",
                     bordercolor=COLORS["border_strong"])
    style.map("Danger.TButton", background=[("active", COLORS["danger_soft"])])

    # NOTE: this Tk build renders Treeview row text in a stray blue when the
    # BUILT-IN "Treeview" style is reconfigured, so every table uses the
    # app-owned "App.Treeview" style (see build_table).
    style.configure("App.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                     foreground=COLORS["text_primary"], font=fonts["table"], rowheight=30, borderwidth=0)
    style.configure("App.Treeview.Heading", background=COLORS["background"], foreground=COLORS["text_secondary"],
                     font=fonts["table_heading"], borderwidth=0, relief="flat", padding=(6, 7))
    style.map("App.Treeview", background=[("selected", COLORS["accent_soft"])],
              foreground=[("selected", COLORS["text_primary"]), ("!selected", COLORS["text_primary"])])

    style.configure("Vertical.TScrollbar", background=COLORS["border"], troughcolor=COLORS["surface"],
                     borderwidth=0, arrowsize=12)

    return fonts


# ---------------------------------------------------------------- cards

def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Card(tk.Canvas):
    """
    White rounded card with a faint shadow, drawn on a Canvas. Put content
    in `card.body`. fit=True: the card grows to its content (use with
    pack(fill="x")). fit=False: the body fills the card (use with
    expand=True for tables).
    """

    def __init__(self, parent, pad=18, radius=16, fill=None, fit=True, page_bg=None, shadow=True):
        page_bg = page_bg or COLORS["background"]
        super().__init__(parent, bg=page_bg, highlightthickness=0, bd=0)
        self._pad, self._radius, self._fit, self._shadow = pad, radius, fit, shadow
        self._fill = fill or COLORS["surface"]
        self.body = tk.Frame(self, bg=self._fill)
        self._win = self.create_window(pad, pad, anchor="nw", window=self.body)
        self.bind("<Configure>", self._on_canvas)
        if fit:
            self.body.bind("<Configure>", self._on_body)
            self.configure(height=40)

    def _on_canvas(self, event):
        w, h = event.width, event.height
        self.delete("bg")
        if self._shadow:
            _round_rect(self, 1, 3, w - 1, h - 1, self._radius, fill=COLORS["shadow"], outline="", tags="bg")
        _round_rect(self, 1, 1, w - 2, h - 3 if self._shadow else h - 2, self._radius,
                    fill=self._fill, outline=COLORS["border"], tags="bg")
        self.tag_lower("bg")
        inner_w = max(w - 2 * self._pad, 1)
        if self._fit:
            self.itemconfigure(self._win, width=inner_w)
        else:
            self.itemconfigure(self._win, width=inner_w, height=max(h - 2 * self._pad - 3, 1))

    def _on_body(self, event):
        self.configure(height=event.height + 2 * self._pad + 3)


def build_panel(parent, title: str, fonts: dict, action=None) -> tk.Frame:
    """Rounded card filling `parent`, with a title row. Returns the content frame."""
    card = Card(parent, fit=False)
    card.pack(fill="both", expand=True)
    surface = card.body
    head = tk.Frame(surface, bg=COLORS["surface"])
    head.pack(fill="x", pady=(0, 10))
    tk.Label(head, text=title, bg=COLORS["surface"], fg=COLORS["text_primary"],
              font=fonts["section_title"]).pack(side="left")
    if action is not None:
        action(head)
    content = tk.Frame(surface, bg=COLORS["surface"])
    content.pack(fill="both", expand=True)
    return content


def form_card(parent, title: str, fonts: dict = None) -> tk.Frame:
    """Rounded card (fit to content) holding a label/field grid. Returns the grid frame."""
    outer = tk.Frame(parent, bg=COLORS["background"])
    outer.pack(fill="x", pady=(0, 16))
    card = Card(outer, fit=True)
    card.pack(fill="x")
    if title:
        tk.Label(card.body, text=title, bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=(fonts or get_fonts_cached())["section_title"]).pack(anchor="w", pady=(0, 8))
    grid = tk.Frame(card.body, bg=COLORS["surface"])
    grid.pack(fill="x")
    grid.columnconfigure(1, weight=1)
    return grid


_fonts_cache = {}


def get_fonts_cached():
    if not _fonts_cache:
        _fonts_cache.update(get_fonts())
    return _fonts_cache


def split_layout(parent, left_width: int = 372):
    """Two columns under the page header: forms on the left, tables on the right."""
    body = tk.Frame(parent, bg=COLORS["background"])
    body.pack(fill="both", expand=True, padx=28, pady=(0, 20))
    body.columnconfigure(0, minsize=left_width, weight=0)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)
    left = tk.Frame(body, bg=COLORS["background"])
    left.grid(row=0, column=0, sticky="new", padx=(0, 16))
    right = tk.Frame(body, bg=COLORS["background"])
    right.grid(row=0, column=1, sticky="nsew")
    return left, right


def section_header(parent, title: str, subtitle: str, fonts: dict):
    wrapper = tk.Frame(parent, bg=COLORS["background"])
    wrapper.pack(fill="x", padx=28, pady=(8, 14))
    tk.Label(wrapper, text=title, bg=COLORS["background"], fg=COLORS["text_primary"],
              font=fonts["header"]).pack(anchor="w")
    if subtitle:
        tk.Label(wrapper, text=subtitle, bg=COLORS["background"], fg=COLORS["text_secondary"],
                  font=fonts["subheader"]).pack(anchor="w", pady=(2, 0))


def form_row(parent, fonts, row_index: int, label_text: str, widget) -> None:
    bg = parent.cget("bg")
    tk.Label(parent, text=label_text, bg=bg, fg=COLORS["text_secondary"],
              font=fonts["label"]).grid(row=row_index, column=0, sticky="w", pady=6, padx=(0, 18))
    widget.grid(row=row_index, column=1, sticky="ew", pady=6)


def button_row(parent, row_index: int = 99) -> tk.Frame:
    row = tk.Frame(parent, bg=parent.cget("bg"))
    row.grid(row=row_index, column=1, sticky="w", pady=(10, 0))
    return row


# ---------------------------------------------------------------- icons

def draw_icon(c: tk.Canvas, name: str, size: int, color: str, bg: str = None):
    """Draw a simple line icon on canvas `c` inside a size x size box."""
    k = size / 24.0
    w = max(round(1.8 * k), 1)

    def r(x1, y1, x2, y2, **kw):
        return c.create_rectangle(x1 * k, y1 * k, x2 * k, y2 * k, **kw)

    def o(x1, y1, x2, y2, **kw):
        return c.create_oval(x1 * k, y1 * k, x2 * k, y2 * k, **kw)

    def ln(*pts, **kw):
        return c.create_line(*[p * k for p in pts], capstyle="round", **kw)

    if name == "grid":
        for x, y in ((4, 4), (14, 4), (4, 14), (14, 14)):
            r(x, y, x + 6, y + 6, fill=color, outline=color)
    elif name == "user":
        o(8, 4, 16, 12, fill=color, outline=color)
        c.create_arc(4 * k, 14 * k, 20 * k, 30 * k, start=0, extent=180, fill=color, outline=color)
    elif name == "users":
        o(4, 6, 11, 13, fill=color, outline=color)
        c.create_arc(1 * k, 15 * k, 14 * k, 29 * k, start=0, extent=180, fill=color, outline=color)
        o(13, 6, 20, 13, fill=color, outline=color)
        c.create_arc(10 * k, 15 * k, 23 * k, 29 * k, start=0, extent=180, fill=color, outline=color)
    elif name == "door":
        r(6, 3, 18, 21, outline=color, width=w)
        o(13.5, 11, 15.5, 13, fill=color, outline=color)
    elif name == "bed":
        ln(3, 7, 3, 19, fill=color, width=w)
        ln(3, 16, 21, 16, 21, 19, fill=color, width=w)
        r(5, 9, 11, 13, fill=color, outline=color)
        r(12, 11, 21, 16, outline=color, width=w)
    elif name == "key":
        o(3, 8, 12, 17, outline=color, width=w)
        ln(12, 12.5, 21, 12.5, fill=color, width=w)
        ln(18, 12.5, 18, 17, fill=color, width=w)
        ln(21, 12.5, 21, 16, fill=color, width=w)
    elif name == "chat":
        _round_rect(c, 3 * k, 4 * k, 21 * k, 16 * k, 3 * k, outline=color, width=w, fill="")
        c.create_polygon(7 * k, 15 * k, 7 * k, 21 * k, 13 * k, 16 * k, fill=color, outline=color)
    elif name == "calendar":
        _round_rect(c, 3.5 * k, 5 * k, 20.5 * k, 20.5 * k, 2.5 * k, outline=color, width=w, fill="")
        r(3.5, 5, 20.5, 9.5, fill=color, outline=color)
        ln(8, 3, 8, 7, fill=color, width=w)
        ln(16, 3, 16, 7, fill=color, width=w)
        for x in (8, 12, 16):
            o(x - 1, 13, x + 1, 15, fill=color, outline=color)
    elif name == "bug":
        o(8, 8, 16, 20, fill=color, outline=color)
        o(9, 4, 15, 9, fill=color, outline=color)
        for y in (10, 14, 18):
            ln(8, y, 4, y - 1.5, fill=color, width=w)
            ln(16, y, 20, y - 1.5, fill=color, width=w)
    elif name == "chart":
        for x1, y1, x2 in ((4, 12, 8.5), (9.5, 7, 14), (15, 3, 19.5)):
            r(x1, y1, x2, 20, fill=color, outline=color)
    elif name == "home":
        c.create_polygon(3 * k, 12 * k, 12 * k, 4 * k, 21 * k, 12 * k, fill=color, outline=color)
        r(6, 12, 18, 20, fill=color, outline=color)
    elif name == "plus":
        ln(12, 5, 12, 19, fill=color, width=w + 1)
        ln(5, 12, 19, 12, fill=color, width=w + 1)
    elif name == "plane":
        c.create_polygon(3 * k, 11 * k, 21 * k, 4 * k, 15 * k, 20 * k, 11 * k, 14 * k,
                         fill=color, outline=color)
    elif name == "clipboard":
        _round_rect(c, 5 * k, 5 * k, 19 * k, 21 * k, 2 * k, outline=color, width=w, fill="")
        r(9, 3, 15, 7, fill=color, outline=color)
        ln(8, 12, 16, 12, fill=color, width=w)
        ln(8, 16, 14, 16, fill=color, width=w)


def icon_tile(parent, icon: str, color: str, size: int = 44, bg: str = None, radius: int = 12) -> tk.Canvas:
    """Colored rounded square with a white icon, like the reference's control tiles."""
    bg = bg or parent.cget("bg")
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    _round_rect(c, 0, 0, size - 1, size - 1, radius, fill=color, outline="")
    inner = int(size * 0.5)
    off = (size - inner) // 2
    sub = tk.Canvas(c, width=inner, height=inner, bg=color, highlightthickness=0, bd=0)
    c.create_window(off, off, anchor="nw", window=sub)
    draw_icon(sub, icon, inner, "#FFFFFF")
    return c


def icon_circle(parent, icon: str, color: str, soft: str, size: int = 40, bg: str = None) -> tk.Canvas:
    """Soft-tinted circle with a colored icon (KPI cards)."""
    bg = bg or parent.cget("bg")
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    c.create_oval(0, 0, size - 1, size - 1, fill=soft, outline="")
    inner = int(size * 0.5)
    off = (size - inner) // 2
    sub = tk.Canvas(c, width=inner, height=inner, bg=soft, highlightthickness=0, bd=0)
    c.create_window(off, off, anchor="nw", window=sub)
    draw_icon(sub, icon, inner, color)
    return c


def nav_icon(parent, icon: str, color: str, bg: str, size: int = 20) -> tk.Canvas:
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    draw_icon(c, icon, size, color)
    return c


def chip(parent, text: str, fg: str, bg: str, font=None) -> tk.Label:
    return tk.Label(parent, text=text, fg=fg, bg=bg, font=font or get_fonts_cached()["small_bold"],
                     padx=8, pady=2)


def initials(name: str) -> str:
    parts = [p for p in str(name).replace("_", " ").split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


# ---------------------------------------------------------------- tables

def build_table(parent, columns, headings, widths, height=10) -> ttk.Treeview:
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=height, style="App.Treeview")
    factor = min(0.75, 520.0 / max(sum(widths), 1))
    for col, label, width in zip(columns, headings, widths):
        tree.heading(col, text=label, anchor="w")
        tree.column(col, width=int(width * factor), minwidth=36, anchor="w", stretch=True)
    return tree


def style_treeview_status_tags(tree: ttk.Treeview):
    """Every row gets a tag ('default' or a status color) so text color is never theme-dependent."""
    tree.tag_configure("default", foreground=COLORS["text_primary"])
    for status, color in STATUS_FG.items():
        tree.tag_configure(f"status_{status.lower()}", foreground=color)


def status_tag(status: str) -> str:
    return f"status_{status.lower()}"


def keep_selection(tree: ttk.Treeview, rebuild) -> None:
    """Run rebuild() (which refills the tree) and re-select the rows that were selected, matched by their first column."""
    wanted = {str(tree.item(item, "values")[0]) for item in tree.selection()}
    rebuild()
    for item in tree.get_children():
        if str(tree.item(item, "values")[0]) in wanted:
            tree.selection_add(item)
            tree.see(item)


def bind_hover(widget, normal_bg: str, hover_bg: str):
    widget.bind("<Enter>", lambda e: widget.configure(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.configure(bg=normal_bg))


# ---------------------------------------------------------------- scrolling

class ScrollFrame(tk.Frame):
    """Vertically scrollable container; put children in `.inner`."""

    def __init__(self, parent, bg=None):
        bg = bg or COLORS["surface"]
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, anchor="nw", window=self.inner)
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        for widget in (self.canvas, self.inner):
            widget.bind("<Enter>", self._bind_wheel)
            widget.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _e):
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))

    def _unbind_wheel(self, _e):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 60) or (-1 if event.delta > 0 else 1), "units")


# ---------------------------------------------------------------- KPI cards

def kpi_row(parent, items, fonts: dict) -> tk.Frame:
    """
    Row of equal KPI cards. items: (label, value, icon, color, soft_color).
    Returns the row frame (children are Cards).
    """
    row = tk.Frame(parent, bg=COLORS["background"])
    for i, (label, value, icon, color, soft) in enumerate(items):
        row.columnconfigure(i, weight=1, uniform="kpi")
        card = Card(row, pad=14, radius=14, fit=True)
        card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0 if i == len(items) - 1 else 6))
        top = tk.Frame(card.body, bg=COLORS["surface"])
        top.pack(fill="x")
        icon_circle(top, icon, color, soft, size=34, bg=COLORS["surface"]).pack(side="left")
        tk.Label(card.body, text=value, bg=COLORS["surface"], fg=COLORS["text_primary"],
                  font=fonts["kpi"]).pack(anchor="w", pady=(8, 0))
        tk.Label(card.body, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=fonts["stat_label"]).pack(anchor="w")
    return row


def build_stat_row(parent, stats, fonts: dict) -> tk.Frame:
    """Compatibility helper: (label, value) pairs as plain KPI cards."""
    palette = [("grid", COLORS["accent"], COLORS["accent_soft"]), ("chart", COLORS["teal"], COLORS["teal_soft"]),
               ("clipboard", COLORS["orange"], COLORS["orange_soft"]), ("bug", COLORS["pink"], COLORS["pink_soft"]),
               ("calendar", COLORS["info"], COLORS["info_soft"])]
    items = [(label, value, *palette[i % len(palette)]) for i, (label, value) in enumerate(stats)]
    row = kpi_row(parent, items, fonts)
    row.pack(fill="x")
    return row
