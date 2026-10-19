"""Timestamps are stored in UTC as 'YYYY-MM-DD HH:MM:SS' (SQLite's own default) and shown in the computer's local time."""
from datetime import datetime, timezone

_FORMAT = "%Y-%m-%d %H:%M:%S"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime(_FORMAT)


def utc_to_local(value):
    """UTC text from the database -> local text for display. Anything unparseable is returned unchanged."""
    if not value or not isinstance(value, str):
        return value
    try:
        parsed = datetime.strptime(value, _FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        return value
    return parsed.astimezone().strftime(_FORMAT)


def localise_rows(rows: list, *columns: str) -> list:
    for row in rows:
        for column in columns:
            if column in row:
                row[column] = utc_to_local(row[column])
    return rows


def local_iso_to_utc(value: str) -> str:
    """Older rows stored local time as ISO text with a 'T'; convert one to the UTC convention."""
    return datetime.fromisoformat(value).astimezone(timezone.utc).strftime(_FORMAT)
