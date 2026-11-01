"""Quality tools shown inside Settings: Six Sigma, variance, Taguchi, FMEA, SIPOC and Poka-Yoke."""
import tkinter as tk
from tkinter import ttk, messagebox

from app.services import fmea_service, poka_yoke_service, sixsigma_service, taguchi_service
from app.theme import (COLORS, Card, build_table, button_row, form_card, form_row, kpi_row, split_layout,
                       style_treeview_status_tags)
from app.utils.exception_handler import handle_unexpected_error
from app.utils.validation import ValidationError


def _pct(value) -> str:
    return f"{value * 100:.2f}%"


def draw_series_chart(canvas: tk.Canvas, fonts, labels, lines, flagged=(), fmt=_pct, empty_text=""):
    """Line chart on a canvas. lines: [{values, color, dash, name}]. Points listed in `flagged` are drawn red."""
    canvas.delete("all")
    w, h = max(canvas.winfo_width(), 320), max(int(canvas["height"]), 120)
    if not labels:
        canvas.create_text(w / 2, h / 2, text=empty_text, fill=COLORS["text_tertiary"], font=fonts["body"], width=w - 40)
        return
    left, right, top, bottom = 62, 18, 24, 30
    top_value = max((v for line in lines for v in line["values"]), default=0) * 1.15 or 1
    pw, ph = w - left - right, h - top - bottom

    def x(i):
        return left + (pw * i / (len(labels) - 1) if len(labels) > 1 else pw / 2)

    def y(v):
        return top + ph - ph * v / top_value

    for i in range(5):
        value = top_value * i / 4
        canvas.create_line(left, y(value), w - right, y(value), fill=COLORS["border"])
        canvas.create_text(left - 8, y(value), text=fmt(value), anchor="e", fill=COLORS["text_tertiary"], font=fonts["small"])
    step = max(1, len(labels) // 8)
    for i in range(0, len(labels), step):
        canvas.create_text(x(i), h - bottom + 14, text=labels[i][5:], fill=COLORS["text_tertiary"], font=fonts["small"])
    for line in lines:
        coords = [c for i, v in enumerate(line["values"]) for c in (x(i), y(v))]
        if len(line["values"]) > 1:
            canvas.create_line(*coords, fill=line["color"], width=2 if not line.get("dash") else 1,
                               dash=line.get("dash"), smooth=False)
        if line.get("points"):
            for i, v in enumerate(line["values"]):
                bad = i in flagged
                canvas.create_oval(x(i) - 4, y(v) - 4, x(i) + 4, y(v) + 4,
                                   fill=COLORS["danger"] if bad else line["color"], outline="")
    lx = left
    for line in lines:
        canvas.create_line(lx, 10, lx + 18, 10, fill=line["color"], dash=line.get("dash"), width=2)
        canvas.create_text(lx + 24, 10, text=line["name"], anchor="w", fill=COLORS["text_secondary"], font=fonts["small"])
        lx += 40 + 7 * len(line["name"])


class _View(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts

    def note(self, text):
        tk.Label(self, text=text, bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["label"],
                 wraplength=900, justify="left", anchor="w").pack(fill="x", pady=(0, 8))

    def chart_card(self, title, height=240):
        card = Card(self, fit=True)
        card.pack(fill="x", pady=(0, 10))
        tk.Label(card.body, text=title, bg=COLORS["surface"], fg=COLORS["text_primary"],
                 font=self.fonts["section_title"]).pack(anchor="w", pady=(0, 6))
        canvas = tk.Canvas(card.body, height=height, bg=COLORS["surface"], highlightthickness=0)
        canvas.pack(fill="x")
        return canvas

    def kpis(self, items):
        if getattr(self, "_kpi", None):
            self._kpi.destroy()
        self._kpi = kpi_row(self, items, self.fonts)
        self._kpi.pack(fill="x", pady=(0, 10), before=self._first_card)

    def run(self, action, label):
        try:
            action()
            self.refresh()
        except ValidationError as e:
            messagebox.showerror(label, str(e))
        except Exception as e:
            handle_unexpected_error("Quality", label, e)


class SixSigmaView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self.note("Opportunity = one logged operation (audit log). Defect = one unexpected error (error log). "
                  "Sigma level uses the usual 1.5 sigma shift. Only real log rows are counted.")
        self.canvas = self.chart_card("Control chart: daily defect rate with 3-sigma limits")
        self._first_card = self.canvas.master.master
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.status = tk.Label(self, text="", bg=COLORS["background"], fg=COLORS["text_secondary"],
                               font=self.fonts["body"], wraplength=900, justify="left", anchor="w")
        self.status.pack(fill="x")

    def _draw(self):
        chart = sixsigma_service.control_chart()
        if not chart["enough"]:
            draw_series_chart(self.canvas, self.fonts, [], [], empty_text=(
                f"Not enough data yet: {chart['days']} day(s) of logged operations, "
                f"{sixsigma_service.MIN_DAYS} needed for a control chart."))
            return
        pts = chart["points"]
        draw_series_chart(self.canvas, self.fonts, [p["day"] for p in pts], [
            {"values": [p["ucl"] for p in pts], "color": COLORS["warning"], "dash": (4, 3), "name": "UCL"},
            {"values": [chart["p_bar"]] * len(pts), "color": COLORS["text_tertiary"], "dash": (2, 2), "name": "Centre"},
            {"values": [p["rate"] for p in pts], "color": COLORS["accent"], "name": "Defect rate", "points": True},
        ], flagged={i for i, p in enumerate(pts) if p["out"]})
        out = chart["out_of_control"]
        self.status.config(text=("Days outside the limits: " + ", ".join(out) + ". Investigate these first.") if out
                           else "No day is outside the 3-sigma limits.")

    def refresh(self):
        s = sixsigma_service.summary()
        sigma = "not measured" if s["sigma"] is None else f"{'≥ ' if s['sigma_is_lower_bound'] else ''}{s['sigma']:.2f}"
        self.kpis([("Operations logged", f"{s['operations']:,}", "clipboard", COLORS["accent"], COLORS["accent_soft"]),
                   ("Errors logged", str(s["defects"]), "bug", COLORS["pink"], COLORS["pink_soft"]),
                   ("DPMO", "not measured" if s["dpmo"] is None else f"{s['dpmo']:,.0f}", "chart", COLORS["orange"], COLORS["orange_soft"]),
                   ("Sigma level", sigma, "grid", COLORS["teal"], COLORS["teal_soft"])])
        self.after(10, self._draw)


class VarianceView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self.note("Variance of the daily defect rate. A rolling window of "
                  f"{sixsigma_service.VARIANCE_WINDOW} days shows whether the process is getting steadier (falling) or less predictable (rising).")
        self.canvas = self.chart_card("Rolling variance of the daily defect rate")
        self._first_card = self.canvas.master.master
        self.canvas.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        v = sixsigma_service.variance_chart()
        if not v["enough"]:
            draw_series_chart(self.canvas, self.fonts, [], [], empty_text=(
                f"Not enough data yet: {v['days']} day(s) of logged operations, {sixsigma_service.MIN_DAYS} needed."))
            return
        roll = v["rolling"]
        draw_series_chart(self.canvas, self.fonts, [r["day"] for r in roll],
                          [{"values": [r["variance"] for r in roll], "color": COLORS["info"], "name": "Variance", "points": True}],
                          fmt=lambda x: f"{x:.5f}")

    def refresh(self):
        v = sixsigma_service.variance_chart()
        ok = v["enough"]
        self.kpis([("Variance", f"{v['variance']:.6f}" if ok else "not measured", "chart", COLORS["info"], COLORS["info_soft"]),
                   ("Standard deviation", _pct(v["std"]) if ok else "not measured", "grid", COLORS["accent"], COLORS["accent_soft"]),
                   ("Mean daily defect rate", _pct(v["mean"]) if ok else "not measured", "bug", COLORS["pink"], COLORS["pink_soft"])])
        self.after(10, self._draw)


class TaguchiView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self.note("Complaint resolution time, smaller is better. S/N = -10·log10(mean of days²), higher is better. "
                  "Loss = (A0 / D0²) · mean of days². D0 and A0 are your own decisions, not measurements.")
        self._first_card = tk.Frame(self, bg=COLORS["background"])
        self._first_card.pack(fill="x")
        bar = tk.Frame(self, bg=COLORS["background"])
        bar.pack(fill="x", pady=(0, 8))
        self.tol_var, self.cost_var = tk.StringVar(), tk.StringVar()
        for text, var, width in (("Tolerance D0 (days)", self.tol_var, 6), ("Cost A0 at D0 (₹, optional)", self.cost_var, 10)):
            tk.Label(bar, text=text, bg=COLORS["background"], fg=COLORS["text_secondary"], font=self.fonts["label"]).pack(side="left", padx=(0, 6))
            ttk.Entry(bar, textvariable=var, width=width).pack(side="left", padx=(0, 14))
        ttk.Button(bar, text="Save", style="Primary.TButton", command=self.on_save).pack(side="left")
        card = Card(self, fit=False)
        card.pack(fill="both", expand=True)
        self.tree = build_table(card.body, ("cat", "n", "mean", "sn", "loss", "flag"),
                                ("Category", "Resolved", "Mean days", "S/N (dB)", "Loss", "Note"),
                                (140, 70, 90, 90, 120, 160), height=8)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)

    def on_save(self):
        self.run(lambda: taguchi_service.set_assumptions(self.tol_var.get(), self.cost_var.get()), "taguchi_save_ui")

    def _loss_text(self, m):
        return f"₹{m['loss_rupees']:,.0f}" if m["loss_rupees"] is not None else f"{m['loss_share'] * 100:.0f}% of A0"

    def refresh(self):
        a = taguchi_service.analyse()
        self.tol_var.set(f"{a['assumptions']['tolerance_days']:g}")
        self.cost_var.set("" if a["assumptions"]["cost"] is None else f"{a['assumptions']['cost']:g}")
        o = a["overall"]
        self.kpis([("Resolved complaints", str(a["resolved"]), "chat", COLORS["accent"], COLORS["accent_soft"]),
                   ("Mean days to resolve", f"{o['mean_days']:.2f}" if o else "not measured", "calendar", COLORS["info"], COLORS["info_soft"]),
                   ("S/N ratio", f"{o['sn']:.1f} dB" if o else "not measured", "chart", COLORS["teal"], COLORS["teal_soft"]),
                   ("Quality loss", self._loss_text(o) if o else "not measured", "clipboard", COLORS["orange"], COLORS["orange_soft"])])
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cat, m in a["categories"].items():
            self.tree.insert("", "end", values=(cat, m["n"], f"{m['mean_days']:.2f}", f"{m['sn']:.1f}", self._loss_text(m),
                                                "few samples" if m["few"] else ""), tags=("default",))


class FmeaView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self._first_card = tk.Frame(self, bg=COLORS["background"])
        self._first_card.pack(fill="x")
        self.note(f"RPN = Severity × Occurrence × Detection (each 1–10). Rows at {fmea_service.RPN_ACTION_THRESHOLD} or more are marked "
                  "'Act' (a team choice you can change in code). Ratings are yours to set and review; "
                  "'Bugs logged' is the real count from the Bug Tracker for the row's module.")
        form = Card(self, fit=True)
        form.pack(fill="x", pady=(0, 10))
        names = ("step", "mode", "effect", "cause", "sev", "occ", "det", "module")
        labels = ("Process step", "Failure mode", "Effect", "Cause", "Severity 1-10", "Occurrence 1-10", "Detection 1-10", "Module")
        self.vars = {n: tk.StringVar() for n in names}
        grid = form.body
        for i, (n, label) in enumerate(zip(names, labels)):
            r, c = divmod(i, 2)
            tk.Label(grid, text=label, bg=COLORS["surface"], fg=COLORS["text_secondary"], font=self.fonts["label"]).grid(
                row=r, column=c * 2, sticky="w", padx=(0 if c == 0 else 18, 8), pady=3)
            ttk.Entry(grid, textvariable=self.vars[n], width=28).grid(row=r, column=c * 2 + 1, sticky="ew", pady=3)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)
        b = tk.Frame(grid, bg=COLORS["surface"])
        b.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(b, text="Add", style="Primary.TButton", command=self.on_add).pack(side="left")
        ttk.Button(b, text="Update ratings of selected", style="Secondary.TButton", command=self.on_update).pack(side="left", padx=(6, 0))
        ttk.Button(b, text="Delete selected", style="Secondary.TButton", command=self.on_delete).pack(side="left", padx=(6, 0))
        card = Card(self, fit=False)
        card.pack(fill="both", expand=True)
        self.tree = build_table(card.body, ("id", "step", "mode", "s", "o", "d", "rpn", "act", "bugs"),
                                ("ID", "Step", "Failure mode", "S", "O", "D", "RPN", "", "Bugs logged"),
                                (36, 110, 190, 30, 30, 30, 50, 44, 80), height=6)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.tag_configure("act", foreground=COLORS["danger"])
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, _e=None):
        sel = self.tree.selection()
        if sel:
            v = self.tree.item(sel[0], "values")
            self.vars["sev"].set(v[3]); self.vars["occ"].set(v[4]); self.vars["det"].set(v[5])

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            raise ValidationError("Select an FMEA row first.")
        return self.tree.item(sel[0], "values")[0]

    def on_add(self):
        v = {k: x.get() for k, x in self.vars.items()}
        self.run(lambda: fmea_service.add_fmea(v["step"], v["mode"], v["effect"], v["cause"], v["sev"], v["occ"],
                                               v["det"], module=v["module"]), "fmea_add_ui")

    def on_update(self):
        self.run(lambda: fmea_service.update_ratings(self._selected(), self.vars["sev"].get(),
                                                      self.vars["occ"].get(), self.vars["det"].get()), "fmea_update_ui")

    def on_delete(self):
        self.run(lambda: fmea_service.delete_fmea(self._selected()), "fmea_delete_ui")

    def refresh(self):
        rows = fmea_service.list_fmea()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in rows:
            self.tree.insert("", "end", values=(r["fmea_id"], r["process_step"], r["failure_mode"], r["severity"],
                                                r["occurrence"], r["detection"], r["rpn"], "Act" if r["act"] else "",
                                                "—" if r["bugs_logged"] is None else r["bugs_logged"]),
                             tags=("act" if r["act"] else "default",))

    def kpis(self, items):
        pass


class SipocView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self.note("Suppliers, Inputs, Process, Outputs, Customers. Pre-filled from how this application actually works; "
                  "edit it to match your TQM SIPOC document.")
        self._first_card = self
        self.left, self.right = split_layout(self, left_width=330)
        form = form_card(self.left, "Add a row", self.fonts)
        self.vars = {n: tk.StringVar() for n in ("s", "i", "p", "o", "c")}
        for i, (n, label) in enumerate(zip(self.vars, ("Supplier", "Input", "Process", "Output", "Customer"))):
            form_row(form, self.fonts, i, label, ttk.Entry(form, textvariable=self.vars[n]))
        b = button_row(form, 5)
        ttk.Button(b, text="Add", style="Primary.TButton", command=self.on_add).pack(side="left")
        ttk.Button(b, text="Delete selected", style="Secondary.TButton", command=self.on_delete).pack(side="left", padx=(6, 0))
        card = Card(self.right, fit=False)
        card.pack(fill="both", expand=True)
        self.tree = build_table(card.body, ("id", "s", "i", "p", "o", "c"),
                                ("ID", "Supplier", "Input", "Process", "Output", "Customer"), (36, 120, 140, 180, 140, 90), height=12)
        self.tree.pack(fill="both", expand=True)

    def kpis(self, items):
        pass

    def on_add(self):
        v = {k: x.get() for k, x in self.vars.items()}
        self.run(lambda: fmea_service.add_sipoc(v["s"], v["i"], v["p"], v["o"], v["c"]), "sipoc_add_ui")

    def on_delete(self):
        sel = self.tree.selection()
        self.run(lambda: fmea_service.delete_sipoc(self.tree.item(sel[0], "values")[0] if sel else None), "sipoc_delete_ui")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in fmea_service.list_sipoc():
            self.tree.insert("", "end", values=(r["sipoc_id"], r["supplier"], r["input"], r["process"], r["output"], r["customer"]),
                             tags=("default",))


class PokaYokeView(_View):
    def __init__(self, parent, fonts):
        super().__init__(parent, fonts)
        self.note("Error-proofing controls built into the application. Evidence is the automated test that proves each one; "
                  "'Proven' turns to 'Missing' if that test is ever deleted or renamed.")
        self._first_card = self
        card = Card(self, fit=False)
        card.pack(fill="both", expand=True)
        self.tree = build_table(card.body, ("area", "kind", "control", "test", "proven"),
                                ("Area", "Type", "Control", "Evidence (test)", "Proven"), (90, 80, 330, 300, 60), height=14)
        self.tree.pack(fill="both", expand=True)
        style_treeview_status_tags(self.tree)
        self.tree.tag_configure("missing", foreground=COLORS["danger"])

    def kpis(self, items):
        pass

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in poka_yoke_service.list_controls():
            self.tree.insert("", "end", values=(c["area"], c["kind"], c["control"], c["test"],
                                                "Proven" if c["proven"] else "Missing"),
                             tags=("default" if c["proven"] else "missing",))
