"""
Taguchi signal-to-noise ratio and quality loss for complaint resolution time (smaller is better).

  y      = days from a complaint being logged to it being resolved
  S/N    = -10 log10(mean(y^2))   (higher is better)
  Loss   = k * mean(y^2), with k = A0 / D0^2

D0 (tolerance, days) and A0 (cost in rupees when resolution takes D0 days) are decisions made by the
hostel, not measured values: they are stored in settings, start at D0 = 3 days with no cost set, and
without A0 the loss is shown as a share of A0 (mean(y^2) / D0^2).
"""
import math
import sqlite3
from datetime import datetime

from app.database.db import get_connection
from app.utils import session
from app.utils.validation import ValidationError

DEFAULT_TOLERANCE_DAYS = 3.0
MIN_SAMPLES = 3
_FLOOR_DAYS = 1 / 1440
_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_assumptions() -> dict:
    session.require_roles(session.ADMIN_ROLES, "view quality measures")
    conn = get_connection()
    try:
        rows = dict(conn.execute("SELECT key, value FROM app_settings WHERE key LIKE 'taguchi:%'").fetchall())
    finally:
        conn.close()
    cost = rows.get("taguchi:cost")
    return {"tolerance_days": float(rows.get("taguchi:tolerance", DEFAULT_TOLERANCE_DAYS)),
            "cost": float(cost) if cost else None}


def set_assumptions(tolerance_days, cost=None) -> dict:
    session.require_roles(session.ADMIN_ROLES, "change quality assumptions")
    try:
        tolerance = float(str(tolerance_days).strip())
    except ValueError:
        raise ValidationError("Tolerance must be a number of days, for example 3.")
    if not 0.1 <= tolerance <= 365:
        raise ValidationError("Tolerance must be between 0.1 and 365 days.")
    cost_value = None
    if cost is not None and str(cost).strip() != "":
        try:
            cost_value = float(str(cost).replace(",", "").strip())
        except ValueError:
            raise ValidationError("Cost must be a number of rupees, for example 500.")
        if not 0 < cost_value <= 10_000_000:
            raise ValidationError("Cost must be more than 0 and at most 1,00,00,000 rupees.")
    conn = get_connection()
    try:
        conn.execute("INSERT INTO app_settings (key, value) VALUES ('taguchi:tolerance', ?) "
                     "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (repr(tolerance),))
        if cost_value is None:
            conn.execute("DELETE FROM app_settings WHERE key = 'taguchi:cost'")
        else:
            conn.execute("INSERT INTO app_settings (key, value) VALUES ('taguchi:cost', ?) "
                         "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (repr(cost_value),))
        conn.commit()
    except sqlite3.Error:
        raise ValidationError("Could not save the assumptions due to a database error.")
    finally:
        conn.close()
    return get_assumptions()


def _days(created: str, resolved: str):
    try:
        delta = datetime.strptime(resolved, _FORMAT) - datetime.strptime(created, _FORMAT)
    except (TypeError, ValueError):
        return None
    return max(delta.total_seconds() / 86400, _FLOOR_DAYS) if delta.total_seconds() >= 0 else None


def _measure(values: list, tolerance: float, cost) -> dict:
    mean_sq = sum(y * y for y in values) / len(values)
    loss_share = mean_sq / (tolerance * tolerance)
    return {"n": len(values), "mean_days": sum(values) / len(values), "sn": -10 * math.log10(mean_sq),
            "loss_share": loss_share, "loss_rupees": loss_share * cost if cost else None,
            "few": len(values) < MIN_SAMPLES}


def analyse() -> dict:
    """Overall and per-category S/N and loss for resolved complaints."""
    assumptions = get_assumptions()
    conn = get_connection()
    try:
        rows = conn.execute("SELECT category, created_at, resolved_at FROM complaints "
                            "WHERE resolved_at IS NOT NULL").fetchall()
    finally:
        conn.close()
    by_category, every = {}, []
    for row in rows:
        y = _days(row["created_at"], row["resolved_at"])
        if y is not None:
            every.append(y)
            by_category.setdefault(row["category"], []).append(y)
    tol, cost = assumptions["tolerance_days"], assumptions["cost"]
    return {"assumptions": assumptions, "resolved": len(every),
            "overall": _measure(every, tol, cost) if every else None,
            "categories": {c: _measure(v, tol, cost) for c, v in sorted(by_category.items())}}
