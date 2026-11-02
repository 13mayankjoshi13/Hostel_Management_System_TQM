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

ACCENT_PRESETS = {
    "Indigo": "#5B50E6", "Teal": "#0F9D8A", "Rose": "#D6336C",
    "Orange": "#E8590C", "Green": "#2F9E44", "Blue": "#1C7ED6",
}
DEFAULT_ACCENT = ACCENT_PRESETS["Indigo"]

_LIGHT_BASE = dict(COLORS)
_DARK_BASE = {
    "background": "#12141C", "surface": "#1B1E2B", "sidebar_bg": "#161926",
    "border": "#2A2E40", "border_strong": "#3A3F55", "shadow": "#0D0F15",
    "text_primary": "#E8EAF2", "text_secondary": "#A5ABBF", "text_tertiary": "#7A8199",
    "success": "#34C268", "success_soft": "#14301F", "danger": "#F0686C", "danger_soft": "#3A1B1D",
    "warning": "#F0A02E", "warning_soft": "#3A2C10", "info": "#5B9BF8", "info_soft": "#14263F",
    "teal": "#2EC4AC", "teal_soft": "#11302B", "pink": "#F06292", "pink_soft": "#3A1827",
    "orange": "#F5A850", "orange_soft": "#3A2A12",
}
_mode = "Light"
_accent = DEFAULT_ACCENT


def _rgb(hex_color: str) -> tuple:
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def _hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in rgb)


def blend(color: str, other: str, amount: float) -> str:
    """`amount` of `other` mixed into `color` (0 = color, 1 = other)."""
    a, b = _rgb(color), _rgb(other)
    return _hex(tuple(x + (y - x) * amount for x, y in zip(a, b)))


def luminance(color: str) -> float:
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def current_appearance() -> tuple:
    return _mode, _accent


def set_appearance(mode: str = "Light", accent: str = DEFAULT_ACCENT) -> None:
    """Switch the whole palette. Call before widgets are built (the main window rebuilds itself)."""
    global _mode, _accent
    _mode, _accent = mode, accent
    dark = mode == "Dark"
    COLORS.update(_LIGHT_BASE)
    if dark:
        COLORS.update(_DARK_BASE)
    surface, background = COLORS["surface"], COLORS["background"]
    COLORS["accent"] = accent
    COLORS["accent_hover"] = blend(accent, "#FFFFFF" if dark else "#000000", 0.15)
    COLORS["accent_soft"] = blend(surface, accent, 0.28 if dark else 0.12)
    hero = blend(accent, "#000000", 0.62 if not dark else 0.72)
    COLORS["hero"] = hero
    COLORS["hero_alt"] = blend(hero, accent, 0.25)
    COLORS["hero_alt2"] = blend(hero, accent, 0.5)
    COLORS["hero_text"] = blend(hero, "#FFFFFF", 0.8)
    COLORS["hero_text2"] = blend(hero, "#FFFFFF", 0.6)
    COLORS["card_bg"] = surface
    COLORS["header_bg"] = background
    COLORS["text_dark"] = COLORS["text_primary"]
    COLORS["text_muted"] = COLORS["text_secondary"]


set_appearance("Light", DEFAULT_ACCENT)

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
    "Unpaid": "#E58A00",
    "Paid": "#16A34A",
    "Waived": "#71717A",
    "Present": "#16A34A",
    "Absent": "#DC2626",
    "Not marked": "#71717A",
    "Inactive": "#71717A",
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

    style.configure("TRadiobutton", background=COLORS["surface"], foreground=COLORS["text_primary"],
                     font=fonts["body"], indicatorcolor=COLORS["surface"])
    style.map("TRadiobutton", background=[("active", COLORS["surface"])],
              indicatorcolor=[("selected", COLORS["accent"])])

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

    try:
        root.bind_all("<MouseWheel>", _dispatch_mousewheel, add="+")
        root.bind_all("<Button-4>", _dispatch_mousewheel, add="+")
        root.bind_all("<Button-5>", _dispatch_mousewheel, add="+")
    except Exception:
        pass

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


def split_layout(parent, left_width: int = 400):
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


_HEADER_ICONS = {
    "Students": "users", "Rooms": "door", "Room Allocation": "key", "Complaints": "chat", "Leave Tracking": "plane",
    "Fines": "clipboard", "Workers": "users", "Bug Tracker": "bug", "User Management": "users", "Notices": "chat",
    "Attendance": "clipboard", "Hostel Events": "calendar", "Wardens & Emergency": "users", "Settings": "gear",
    "My Room": "home", "My Complaints": "chat", "My Leave": "plane", "My Fines": "clipboard",
    "My Notices": "chat", "My Details": "user", "Calendar": "calendar",
}


def section_header(parent, title: str, subtitle: str, fonts: dict):
    wrapper = tk.Frame(parent, bg=COLORS["background"])
    wrapper.pack(fill="x", padx=28, pady=(8, 14))
    icon_tile(wrapper, _HEADER_ICONS.get(title, "grid"), COLORS["accent"], size=44,
              bg=COLORS["background"]).pack(side="left", padx=(0, 14))
    text = tk.Frame(wrapper, bg=COLORS["background"])
    text.pack(side="left")
    tk.Label(text, text=title, bg=COLORS["background"], fg=COLORS["text_primary"],
              font=fonts["header"]).pack(anchor="w")
    if subtitle:
        tk.Label(text, text=subtitle, bg=COLORS["background"], fg=COLORS["text_secondary"],
                  font=fonts["subheader"]).pack(anchor="w", pady=(2, 0))


def form_row(parent, fonts, row_index: int, label_text: str, widget) -> None:
    bg = parent.cget("bg")
    tk.Label(parent, text=label_text, bg=bg, fg=COLORS["text_secondary"],
              font=fonts["label"]).grid(row=row_index, column=0, sticky="w", pady=6, padx=(0, 18))
    widget.grid(row=row_index, column=1, sticky="ew", pady=6)


def button_row(parent, row_index: int = 99) -> tk.Frame:
    row = tk.Frame(parent, bg=parent.cget("bg"))
    row.grid(row=row_index, column=0, columnspan=2, sticky="w", pady=(10, 0))
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
    elif name == "gear":
        c.create_oval(7 * k, 7 * k, 17 * k, 17 * k, outline=color, width=w + 1, fill="")
        for x1, y1, x2, y2 in ((12, 3, 12, 6), (12, 18, 12, 21), (3, 12, 6, 12), (18, 12, 21, 12)):
            ln(x1, y1, x2, y2, fill=color, width=w + 1)
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


# ---------------------------------------------------------------- universal mousewheel

def _dispatch_mousewheel(event):
    """Universal mousewheel scroll: dynamically finds whatever scrollable widget is under the cursor."""
    try:
        x, y = getattr(event, "x_root", 0), getattr(event, "y_root", 0)
        target = event.widget.winfo_containing(x, y) if getattr(event, "widget", None) else None
    except Exception:
        target = getattr(event, "widget", None)
    if target is None:
        return
    delta = int(-1 * (event.delta / 120)) * 2 if getattr(event, "delta", 0) else (
        2 if getattr(event, "num", None) == 5 else -2
    )
    curr = target
    while curr is not None:
        try:
            if isinstance(curr, ttk.Treeview):
                curr.yview_scroll(delta, "units")
                return "break"
            if isinstance(curr, tk.Text):
                curr.yview_scroll(delta, "units")
                return "break"
            if hasattr(curr, "_scroll_canvas"):
                curr._scroll_canvas.yview_scroll(delta, "units")
                return "break"
            if isinstance(curr, tk.Canvas) and str(curr.cget("scrollregion")).strip():
                curr.yview_scroll(delta, "units")
                return "break"
            curr = getattr(curr, "master", None)
        except Exception:
            break


# ---------------------------------------------------------------- tables

class ScrollableTreeview(ttk.Treeview):
    """Treeview that comes pre-packaged with a vertical Scrollbar and mousewheel support."""

    def __init__(self, parent, *args, **kwargs):
        bg = COLORS["surface"]
        try:
            if hasattr(parent, "cget"):
                bg = parent.cget("bg")
        except Exception:
            pass
        self._container = tk.Frame(parent, bg=bg)
        super().__init__(self._container, *args, **kwargs)
        self._scrollbar = ttk.Scrollbar(self._container, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        super().pack(side="left", fill="both", expand=True)
        self.bind("<MouseWheel>", self._on_tree_wheel)
        self.bind("<Button-4>", lambda e: self.yview_scroll(-2, "units"))
        self.bind("<Button-5>", lambda e: self.yview_scroll(2, "units"))

    def _on_tree_wheel(self, event):
        delta = int(-1 * (event.delta / 120)) * 2 if getattr(event, "delta", 0) else (
            2 if getattr(event, "num", None) == 5 else -2
        )
        self.yview_scroll(delta, "units")
        return "break"

    def pack(self, *args, **kwargs):
        self._container.pack(*args, **kwargs)

    def pack_forget(self):
        self._container.pack_forget()

    def pack_info(self):
        return self._container.pack_info()

    def grid(self, *args, **kwargs):
        self._container.grid(*args, **kwargs)

    def grid_forget(self):
        self._container.grid_forget()

    def place(self, *args, **kwargs):
        self._container.place(*args, **kwargs)

    def place_forget(self):
        self._container.place_forget()

    def winfo_ismapped(self):
        return self._container.winfo_ismapped()

    def destroy(self):
        try:
            self._container.destroy()
        except Exception:
            pass
        try:
            super().destroy()
        except Exception:
            pass


def build_table(parent, columns, headings, widths, height=10) -> ttk.Treeview:
    tree = ScrollableTreeview(parent, columns=columns, show="headings", height=height, style="App.Treeview")
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


def make_clickable(widget, command, hover_bg=None, normal_bg=None):
    """Recursively set cursor to hand2 and bind Button-1 to command for widget and all descendants."""
    try:
        widget.configure(cursor="hand2")
    except Exception:
        pass
    widget.bind("<Button-1>", lambda e: command())
    if hover_bg and normal_bg:
        widget.bind("<Enter>", lambda e: widget.configure(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.configure(bg=normal_bg))
    for child in widget.winfo_children():
        make_clickable(child, command, hover_bg, normal_bg)


def show_detail_dialog(parent=None, title: str = "Details", subtitle: str = "", icon: str = "clipboard", color: str = None,
                       fields=None, action_btn_text: str = None, on_action=None, **kwargs):
    """Modern modal dialog showing structured details (Notice, Event, Complaint, etc.)."""
    if isinstance(parent, str):
        title, parent = parent, None

    title = kwargs.get("title", title)
    subtitle = kwargs.get("subtitle", subtitle)
    icon = kwargs.get("icon", icon)
    color = kwargs.get("color", color) or COLORS.get("accent", "#5B50E6")
    fields = kwargs.get("fields", fields) or []
    action_btn_text = kwargs.get("action_btn_text", action_btn_text)
    on_action = kwargs.get("on_action", on_action)
    full_text = kwargs.get("full_text")

    if isinstance(fields, dict):
        fields = list(fields.items())
    elif isinstance(fields, (list, tuple)):
        fields = list(fields)
    else:
        fields = []

    if full_text and not any(k.lower() in ("description", "details", "notice message", "message", "full content") for k, _ in fields):
        fields.append(("Details", str(full_text)))

    root = tk._default_root
    target_parent = parent if parent is not None and hasattr(parent, "winfo_toplevel") else root

    dlg = tk.Toplevel(target_parent)
    dlg.title(title)
    dlg.configure(bg=COLORS["surface"])
    dlg.resizable(False, False)
    if target_parent is not None:
        try:
            dlg.transient(target_parent.winfo_toplevel())
        except Exception:
            pass
    fonts = get_fonts_cached()

    w, h = 540, 440
    dlg.update_idletasks()
    try:
        top = target_parent.winfo_toplevel() if target_parent else None
        pw = top.winfo_width() if top else 800
        ph = top.winfo_height() if top else 600
        px = top.winfo_rootx() if top else 100
        py = top.winfo_rooty() if top else 100
    except Exception:
        pw, ph, px, py = 800, 600, 100, 100
    x = max(0, px + (pw - w) // 2)
    y = max(0, py + (ph - h) // 2)
    dlg.geometry(f"{w}x{h}+{x}+{y}")

    head = tk.Frame(dlg, bg=COLORS["background"], padx=20, pady=16)
    head.pack(fill="x")
    icon_tile(head, icon, color, size=40, bg=COLORS["background"]).pack(side="left", padx=(0, 14))
    tframe = tk.Frame(head, bg=COLORS["background"])
    tframe.pack(side="left", fill="both", expand=True)
    tk.Label(tframe, text=title, bg=COLORS["background"], fg=COLORS["text_primary"],
             font=fonts["header"], anchor="w").pack(anchor="w")
    if subtitle:
        tk.Label(tframe, text=subtitle, bg=COLORS["background"], fg=COLORS["text_secondary"],
                 font=fonts["small"], anchor="w").pack(anchor="w", pady=(2, 0))

    body_frame = tk.Frame(dlg, bg=COLORS["surface"], padx=24, pady=16)
    body_frame.pack(fill="both", expand=True)

    for label, val in fields:
        row = tk.Frame(body_frame, bg=COLORS["surface"], pady=4)
        row.pack(fill="x")
        tk.Label(row, text=str(label).upper(), bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                 font=fonts["small_bold"], width=13, anchor="w").pack(side="left", anchor="nw")
        if "\n" in str(val) or len(str(val)) > 55:
            txt = tk.Text(row, bg=COLORS["background"], fg=COLORS["text_primary"],
                          font=fonts["body"], wrap="word", relief="flat", padx=8, pady=8, height=6)
            txt.insert("1.0", str(val))
            txt.configure(state="disabled")
            txt.pack(side="left", fill="both", expand=True)
        else:
            tk.Label(row, text=str(val), bg=COLORS["surface"], fg=COLORS["text_primary"],
                     font=fonts["body"], anchor="w", justify="left").pack(side="left", fill="x", expand=True)

    foot = tk.Frame(dlg, bg=COLORS["surface"], padx=24, pady=14)
    foot.pack(fill="x")
    ttk.Button(foot, text="Close", style="Secondary.TButton", command=dlg.destroy).pack(side="right")
    if action_btn_text and on_action:
        def do_action():
            dlg.destroy()
            on_action()
        ttk.Button(foot, text=action_btn_text, style="Primary.TButton", command=do_action).pack(side="right", padx=(0, 8))

    try:
        dlg.grab_set()
    except Exception:
        pass
    return dlg


# ---------------------------------------------------------------- scrolling

class ScrollFrame(tk.Frame):
    """Vertically scrollable container; put children in `.inner`."""

    def __init__(self, parent, bg=None):
        bg = bg or COLORS["surface"]
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, anchor="nw", window=self.inner)

        self.canvas._scroll_canvas = self.canvas
        self.inner._scroll_canvas = self.canvas
        self._scroll_canvas = self.canvas

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))

    def update_scroll(self):
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


# ---------------------------------------------------------------- KPI cards

def kpi_row(parent, items, fonts: dict) -> tk.Frame:
    """
    Row of equal KPI cards. items: (label, value, icon, color, soft_color[, on_click]).
    Returns the row frame (children are Cards).
    """
    row = tk.Frame(parent, bg=COLORS["background"])
    for i, itm in enumerate(items):
        label, value, icon, color, soft = itm[:5]
        on_click = itm[5] if len(itm) > 5 else None
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
        if on_click:
            make_clickable(card, on_click)
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
