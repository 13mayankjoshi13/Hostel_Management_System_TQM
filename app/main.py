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


def run():
    try:
        initialize_database()
    except Exception as exc:
        log_error("Database", type(exc).__name__, "Critical",
                   "initialize_database", status="Open", message_reference=str(exc))
        print(f"Fatal error initializing the database: {exc}", file=sys.stderr)
        return

    try:
        from app.ui.main_window import MainWindow
        app = MainWindow()
        app.mainloop()
    except Exception as exc:
        log_error("Application", type(exc).__name__, "Critical",
                   "run", status="Open", message_reference=str(exc))
        print("An unexpected error occurred:", file=sys.stderr)
        traceback.print_exc()
