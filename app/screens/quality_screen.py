"""
Quality Monitoring screen (SQC automation).

Everything drawn here comes from quality_service, which reads real bug
records — nothing is sample/placeholder data. With zero bugs logged,
the charts show an honest "not enough data yet" message instead of a
fabricated example, in keeping with the project's "do not fabricate
quality results" rule.

Charts are drawn directly on a tk.Canvas (no charting library) to keep
the project dependency-free, as stated in requirements.txt.
"""
import tkinter as tk
from tkinter import ttk

from app.services import quality_service
from app.theme import COLORS, section_header, build_panel, build_stat_row

_FISHBONE_COLORS = {
    "People": "#B45309", "Process": "#1D4ED8", "Software/Code": "#3457D5",
    "Database": "#15803D", "Infrastructure": "#71717A", "Measurement": "#B91C1C",
}


class QualityScreen(tk.Frame):
    def __init__(self, parent, fonts):
        super().__init__(parent, bg=COLORS["background"])
        self.fonts = fonts
        section_header(self, "Quality Monitoring",
                        "SQC tools generated live from real bug records — nothing on this page is sample data.",
                        fonts)

        self.stats_slot = tk.Frame(self, bg=COLORS["background"])
        self.stats_slot.pack(fill="x", padx=28, pady=(0, 20))

        charts_wrapper = tk.Frame(self, bg=COLORS["background"])
        charts_wrapper.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        pareto_wrap = tk.Frame(charts_wrapper, bg=COLORS["background"])
        pareto_wrap.pack(fill="both", expand=True, pady=(0, 20))
        pareto_content = build_panel(pareto_wrap, "Pareto Chart — Defects by Category", self.fonts)
        self.pareto_canvas = tk.Canvas(pareto_content, height=200, bg=COLORS["surface"],
                                         highlightthickness=0)
        self.pareto_canvas.pack(fill="both", expand=True)

        fishbone_wrap = tk.Frame(charts_wrapper, bg=COLORS["background"])
        fishbone_wrap.pack(fill="both", expand=True)
        fishbone_content = build_panel(fishbone_wrap, "Fishbone Diagram — Cause and Effect", self.fonts)
        self.fishbone_canvas = tk.Canvas(fishbone_content, height=260, bg=COLORS["surface"],
                                           highlightthickness=0)
        self.fishbone_canvas.pack(fill="both", expand=True)

        self.pareto_canvas.bind("<Configure>", lambda e: self._draw_pareto())
        self.fishbone_canvas.bind("<Configure>", lambda e: self._draw_fishbone())

        self.refresh()

    # ---- KPI strip ----

    def _refresh_stats(self):
        for w in self.stats_slot.winfo_children():
            w.destroy()
        s = quality_service.get_quality_summary()
        build_stat_row(self.stats_slot, [
            ("Total Bugs", str(s["total"])),
            ("Open", str(s["open"])),
            ("In Progress", str(s["in_progress"])),
            ("Fixed", str(s["fixed"])),
            ("Closed", str(s["closed"])),
            ("Fix Rate", f"{s['fix_rate_pct']}%"),
        ], self.fonts)

    # ---- Pareto chart ----

    def _draw_pareto(self):
        c = self.pareto_canvas
        c.update_idletasks()
        width, height = c.winfo_width(), c.winfo_height()
        if width <= 1 or height <= 1:
            self.after(50, self._draw_pareto)
            return
        c.delete("all")

        data = quality_service.get_pareto_data()
        if not data:
            c.create_text(width / 2, height / 2, text="No bugs logged yet — nothing to chart.",
                           fill=COLORS["text_tertiary"], font=self.fonts["body"])
            return

        pad_left, pad_right, pad_top, pad_bottom = 46, 46, 20, 40
        plot_w = width - pad_left - pad_right
        plot_h = height - pad_top - pad_bottom
        max_count = max(count for _, count, _ in data)
        bar_slot = plot_w / len(data)
        bar_w = min(bar_slot * 0.5, 64)

        # axes
        c.create_line(pad_left, pad_top, pad_left, pad_top + plot_h,
                       fill=COLORS["border_strong"])
        c.create_line(pad_left, pad_top + plot_h, pad_left + plot_w, pad_top + plot_h,
                       fill=COLORS["border_strong"])

        points = []
        for i, (category, count, cum_pct) in enumerate(data):
            x_center = pad_left + bar_slot * i + bar_slot / 2
            bar_h = (count / max_count) * plot_h if max_count else 0
            y_top = pad_top + plot_h - bar_h
            c.create_rectangle(x_center - bar_w / 2, y_top, x_center + bar_w / 2,
                                pad_top + plot_h, fill=COLORS["accent"], width=0)
            c.create_text(x_center, y_top - 10, text=str(count),
                          fill=COLORS["text_primary"], font=self.fonts["label"])
            c.create_text(x_center, pad_top + plot_h + 14, text=category,
                          fill=COLORS["text_secondary"], font=self.fonts["label"], width=bar_slot)

            y_cum = pad_top + plot_h - (cum_pct / 100) * plot_h
            points.append((x_center, y_cum))

        # cumulative % line
        for i in range(len(points) - 1):
            c.create_line(*points[i], *points[i + 1], fill=COLORS["warning"], width=2)
        for x, y in points:
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=COLORS["warning"], width=0)

        c.create_text(pad_left - 10, pad_top, text="100%", anchor="e",
                      fill=COLORS["text_tertiary"], font=self.fonts["label"])
        c.create_text(pad_left - 10, pad_top + plot_h, text="0%", anchor="e",
                      fill=COLORS["text_tertiary"], font=self.fonts["label"])

    # ---- Fishbone diagram ----

    def _draw_fishbone(self):
        c = self.fishbone_canvas
        c.update_idletasks()
        width, height = c.winfo_width(), c.winfo_height()
        if width <= 1 or height <= 1:
            self.after(50, self._draw_fishbone)
            return
        c.delete("all")

        data = quality_service.get_fishbone_data()
        has_any = any(causes for causes in data.values())

        spine_y = height / 2
        spine_x_start = 70
        spine_x_end = width - 140
        c.create_line(spine_x_start, spine_y, spine_x_end, spine_y,
                       fill=COLORS["text_secondary"], width=2)
        c.create_polygon(spine_x_end, spine_y - 8, spine_x_end, spine_y + 8, spine_x_end + 16, spine_y,
                          fill=COLORS["text_secondary"], width=0)
        c.create_rectangle(spine_x_end + 20, spine_y - 22, width - 16, spine_y + 22,
                            outline=COLORS["text_primary"], width=1, fill=COLORS["surface"])
        c.create_text((spine_x_end + 20 + width - 16) / 2, spine_y, text="Reduce\nBugs",
                      fill=COLORS["text_primary"], font=self.fonts["label"], justify="center")

        branches = quality_service.FISHBONE_BRANCHES
        top_branches = branches[:3]
        bottom_branches = branches[3:]
        branch_span = (spine_x_end - spine_x_start) / 3

        # Fixed attachment height for every diagonal, regardless of how
        # many causes a branch has, so branches stay visually aligned.
        # Label sits above that point; causes stack between the two,
        # closest to the attachment point so they never collide with
        # the label even when a branch has the maximum number shown.
        top_attach_y = min(100, spine_y - 36)
        bottom_attach_y = max(height - 100, spine_y + 36)
        label_margin = 14

        if not has_any:
            c.create_text(width / 2, height - 14,
                          text="No bugs logged yet — branches will populate with real causes once bugs exist.",
                          fill=COLORS["text_tertiary"], font=self.fonts["label"])

        for i, name in enumerate(top_branches):
            bx = spine_x_start + branch_span * (i + 0.7)
            c.create_line(bx, top_attach_y, spine_x_start + branch_span * (i + 1), spine_y,
                           fill=_FISHBONE_COLORS[name], width=2)
            c.create_text(bx, label_margin, text=name, fill=_FISHBONE_COLORS[name],
                          font=self.fonts["label"], anchor="n")
            self._draw_causes(c, bx, label_margin + 20, top_attach_y - 6,
                               data.get(name, []), top_to_bottom=True)

        for i, name in enumerate(bottom_branches):
            bx = spine_x_start + branch_span * (i + 0.7)
            c.create_line(bx, bottom_attach_y, spine_x_start + branch_span * (i + 1), spine_y,
                           fill=_FISHBONE_COLORS[name], width=2)
            c.create_text(bx, height - label_margin, text=name, fill=_FISHBONE_COLORS[name],
                          font=self.fonts["label"], anchor="s")
            self._draw_causes(c, bx, bottom_attach_y + 6, height - label_margin - 20,
                               data.get(name, []), top_to_bottom=False)

    def _draw_causes(self, c, bx, range_start, range_end, causes, top_to_bottom: bool, limit: int = 2):
        """
        Stack cause bullets between a branch's label and its diagonal
        attachment point, never overlapping either. range_start is
        always the end closest to the attachment point and range_end
        the end closest to the label, with range_start < range_end in
        canvas-y terms for both top and bottom branches — so the same
        incrementing step works for both.
        """
        if not causes:
            return
        step = min(13, max(10, (range_end - range_start) / max(limit, 1)))
        for i, title in enumerate(causes[:limit]):
            text = title if len(title) <= 24 else title[:22] + "…"
            y = range_start + step * i
            c.create_text(bx, y, text=f"• {text}", fill=COLORS["text_secondary"],
                          font=self.fonts["label"], anchor="center")
        if len(causes) > limit:
            y = range_start + step * limit
            c.create_text(bx, min(y, range_end), text=f"(+{len(causes) - limit} more)",
                          fill=COLORS["text_tertiary"], font=self.fonts["label"])

    def refresh(self):
        self._refresh_stats()
        self.after(10, self._draw_pareto)
        self.after(10, self._draw_fishbone)
