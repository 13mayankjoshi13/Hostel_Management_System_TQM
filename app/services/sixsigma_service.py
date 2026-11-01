"""
Six Sigma and variance, measured from the application's own logs.

Definitions (stated on screen too, so nobody reads more into the numbers than they say):
  - Opportunity = one logged operation (a row in the audit log).
  - Defect      = one unexpected error (a row in the error log) on that day.
  - DPMO        = defects / opportunities x 1,000,000.
  - Sigma level = normal quantile of the yield + the conventional 1.5 sigma shift.
Nothing is estimated: with no logged operations there is no result, and with fewer than
MIN_DAYS days of data the charts say so instead of drawing a line.
"""
import csv
import math
from statistics import NormalDist, pvariance, variance

from app.utils import logging_service as ls
from app.utils import session

MIN_DAYS = 5
SIGMA_SHIFT = 1.5
VARIANCE_WINDOW = 5


def _day_counts(path: str) -> dict:
    counts = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                day = (row.get("timestamp") or "")[:10]
                if len(day) == 10:
                    counts[day] = counts.get(day, 0) + 1
    except (OSError, csv.Error):
        pass
    return counts


def daily_series() -> list:
    """[{day, operations, defects, rate}] for every day that has at least one logged operation."""
    session.require_roles(session.ADMIN_ROLES, "view quality measures")
    operations = _day_counts(ls.AUDIT_LOG_CSV)
    defects = _day_counts(ls.ERROR_LOG_CSV)
    series = []
    for day in sorted(operations):
        n, d = operations[day], defects.get(day, 0)
        series.append({"day": day, "operations": n, "defects": d, "rate": d / n})
    return series


def sigma_level(dpmo: float):
    """Short-term sigma for a DPMO, or None when it cannot be computed."""
    if dpmo is None or dpmo <= 0 or dpmo >= 1_000_000:
        return None
    return NormalDist().inv_cdf(1 - dpmo / 1_000_000) + SIGMA_SHIFT


def summary() -> dict:
    series = daily_series()
    operations = sum(s["operations"] for s in series)
    defects = sum(s["defects"] for s in series)
    result = {"days": len(series), "operations": operations, "defects": defects,
              "dpmo": None, "sigma": None, "sigma_is_lower_bound": False, "enough": len(series) >= MIN_DAYS}
    if operations == 0:
        return result
    result["dpmo"] = defects / operations * 1_000_000
    if defects:
        result["sigma"] = sigma_level(result["dpmo"])
    else:
        result["sigma"] = sigma_level(1_000_000 / operations)
        result["sigma_is_lower_bound"] = True
    return result


def control_chart() -> dict:
    """p-chart of the daily defect rate. Limits are 3 standard errors around the overall rate."""
    series = daily_series()
    if len(series) < MIN_DAYS:
        return {"enough": False, "days": len(series), "points": []}
    total_n = sum(s["operations"] for s in series)
    p_bar = sum(s["defects"] for s in series) / total_n
    points, out = [], []
    for s in series:
        se = math.sqrt(p_bar * (1 - p_bar) / s["operations"])
        ucl, lcl = min(1.0, p_bar + 3 * se), max(0.0, p_bar - 3 * se)
        flagged = s["rate"] > ucl or s["rate"] < lcl
        points.append({**s, "ucl": ucl, "lcl": lcl, "out": flagged})
        if flagged:
            out.append(s["day"])
    return {"enough": True, "days": len(series), "p_bar": p_bar, "points": points, "out_of_control": out}


def variance_chart() -> dict:
    """Variance of the daily defect rate, overall and as a rolling window."""
    series = daily_series()
    if len(series) < MIN_DAYS:
        return {"enough": False, "days": len(series), "rolling": []}
    rates = [s["rate"] for s in series]
    rolling = [{"day": series[i]["day"], "variance": pvariance(rates[i - VARIANCE_WINDOW + 1:i + 1])}
               for i in range(VARIANCE_WINDOW - 1, len(rates))]
    return {"enough": True, "days": len(series), "variance": variance(rates), "std": math.sqrt(variance(rates)),
            "mean": sum(rates) / len(rates), "rolling": rolling, "window": VARIANCE_WINDOW}
