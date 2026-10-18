"""Daily database backups with automatic pruning, plus restore. CLI: python -m app.database.backup [list|restore FILE]"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime

from app.database import db as db_module
from app.utils.logging_service import log_audit, log_error

KEEP_BACKUPS = 7
_PREFIX = "hostel_"


def backup_dir(db_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "backups")


def list_backups(db_path: str = None) -> list:
    db_path = db_path or db_module.DATABASE_PATH
    folder = backup_dir(db_path)
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, n) for n in os.listdir(folder)
                  if n.startswith(_PREFIX) and n.endswith(".db"))


def _is_healthy(path: str) -> bool:
    try:
        conn = sqlite3.connect(path)
        try:
            return conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def create_backup(db_path: str = None, keep: int = KEEP_BACKUPS):
    """One backup per calendar day. A damaged database is never backed up, so it cannot push out good copies."""
    db_path = db_path or db_module.DATABASE_PATH
    if not os.path.exists(db_path):
        return None
    today = datetime.now().strftime("%Y%m%d")
    if any(os.path.basename(p).startswith(f"{_PREFIX}{today}") for p in list_backups(db_path)):
        return None
    if not _is_healthy(db_path):
        log_error("Database", "IntegrityError", "Critical", "create_backup",
                   status="Open", message_reference="Database failed its integrity check; backup skipped.")
        return None
    folder = backup_dir(db_path)
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, f"{_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    source = sqlite3.connect(db_path)
    try:
        dest = sqlite3.connect(target)
        try:
            source.backup(dest)
        finally:
            dest.close()
    finally:
        source.close()
    for old in list_backups(db_path)[:-keep]:
        os.remove(old)
    log_audit("Database", "Backup", os.path.basename(target), "Success", "Daily database backup created.")
    return target


def restore_backup(backup_path: str, db_path: str = None) -> str:
    """Replace the database with a backup. The current file is kept next to it as *.before_restore."""
    db_path = db_path or db_module.DATABASE_PATH
    if not os.path.isfile(backup_path) or not _is_healthy(backup_path):
        raise ValueError("That backup file is missing or damaged.")
    saved = None
    if os.path.exists(db_path):
        saved = db_path + ".before_restore"
        shutil.copy2(db_path, saved)
    shutil.copy2(backup_path, db_path)
    log_audit("Database", "Restore", os.path.basename(backup_path), "Success", "Database restored from backup.")
    return saved or ""


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["restore"] and len(args) == 2:
        restore_backup(args[1])
        print(f"Restored from {args[1]}.")
    else:
        for path in list_backups():
            print(path)
