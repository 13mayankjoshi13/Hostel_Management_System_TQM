"""Appearance settings (light/dark and accent colour), saved per user, plus the last choice for the login screen."""
import re
import sqlite3

from app.database.db import get_connection
from app.utils import session
from app.utils.validation import ValidationError

MODES = ("Light", "Dark")
DEFAULT = ("Light", "#5B50E6")
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
_MAX_LIGHTNESS = 0.45


def validate_appearance(mode: str, accent: str) -> tuple:
    from app.theme import luminance

    if mode not in MODES:
        raise ValidationError("Theme must be Light or Dark.")
    accent = (accent or "").strip()
    if not _HEX.match(accent):
        raise ValidationError("Enter the colour as #RRGGBB, for example #5B50E6.")
    accent = accent.upper()
    if luminance(accent) > _MAX_LIGHTNESS:
        raise ValidationError("That colour is too light for white button text. Pick a darker colour.")
    return mode, accent


def _read(conn, key):
    row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def get_appearance(username: str = None) -> tuple:
    """The user's saved (mode, accent); with no username, the last choice made on this computer."""
    key = f"appearance:{username}" if username else "appearance:last"
    try:
        conn = get_connection()
    except sqlite3.Error:
        return DEFAULT
    try:
        value = _read(conn, key)
        if value is None and username:
            value = _read(conn, "appearance:last")
        if not value:
            return DEFAULT
        mode, _, accent = value.partition("|")
        return validate_appearance(mode, accent)
    except (sqlite3.Error, ValidationError):
        return DEFAULT
    finally:
        conn.close()


def set_appearance(mode: str, accent: str) -> tuple:
    if not session.is_logged_in():
        raise ValidationError("Please log in to change the appearance.")
    mode, accent = validate_appearance(mode, accent)
    conn = get_connection()
    try:
        for key in (f"appearance:{session.get_user()}", "appearance:last"):
            conn.execute("INSERT INTO app_settings (key, value) VALUES (?, ?) "
                         "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, f"{mode}|{accent}"))
        conn.commit()
        return mode, accent
    except sqlite3.Error:
        raise ValidationError("Could not save the appearance due to a database error.")
    finally:
        conn.close()
