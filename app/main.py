"""
Application bootstrap.

Responsibilities:
1. Initialize the SQLite database (idempotent).
2. Launch the Tkinter GUI.
3. Provide a top-level safety net: any exception that escapes the GUI's
   own handlers is caught here, logged, and reported cleanly instead of
   dumping a traceback to the console.
"""
import sys
import traceback

from app.database.db import initialize_database
from app.utils.logging_service import log_error


def show_fatal(title: str, message: str) -> None:
    """Tell the user in a window: the app is normally started without a console, so stderr is never seen."""
    print(f"{title}: {message}", file=sys.stderr)
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass


def run():
    try:
        from app.database.backup import create_backup
        create_backup()
    except Exception as exc:
        log_error("Database", type(exc).__name__, "High", "create_backup",
                   status="Open", message_reference=str(exc))

    try:
        initialize_database()
    except Exception as exc:
        error_id = log_error("Database", type(exc).__name__, "Critical",
                              "initialize_database", status="Open", message_reference=str(exc))
        show_fatal("Hostel Management System",
                   f"The database could not be opened, so the application cannot start.\n\n"
                   f"{exc}\n\nLogged as {error_id}. Check that the file is not locked by another program "
                   f"or damaged. If it is damaged, restore the latest copy from app/database/backups with "
                   f"python -m app.database.backup restore <file>.")
        return

    try:
        from app.database.check_data import run_checks, log_issues
        log_issues(run_checks())
    except Exception as exc:
        log_error("Database", type(exc).__name__, "Medium", "check_data",
                   status="Open", message_reference=str(exc))

    try:
        from app.services.auth_service import ensure_default_admin
        ensure_default_admin()
    except Exception as exc:
        log_error("Auth", type(exc).__name__, "Critical",
                   "ensure_default_admin", status="Open", message_reference=str(exc))

    try:
        from app.services.event_service import ensure_default_holidays
        ensure_default_holidays()
    except Exception as exc:
        log_error("Calendar", type(exc).__name__, "Medium",
                   "ensure_default_holidays", status="Open", message_reference=str(exc))

    try:
        from app.screens.main_window import MainWindow
        app = MainWindow()
        app.mainloop()
    except Exception as exc:
        error_id = log_error("Application", type(exc).__name__, "Critical",
                              "run", status="Open", message_reference=str(exc))
        traceback.print_exc()
        show_fatal("Hostel Management System",
                   f"The application hit an unexpected error and has to close.\n\nLogged as {error_id}.")
