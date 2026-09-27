"""
Exception Handling (Q09 feature #1).

Central handler for anything NOT already caught as an expected
ValidationError. Its job:

    Exception -> log to TQM/data/error_logs.csv -> friendly message to user

No unexpected exception should ever crash the application or show a raw
Python traceback to a user.
"""
from tkinter import messagebox

from app.utils.logging_service import log_error


def handle_unexpected_error(module: str, action: str, exc: Exception) -> str:
    """
    Log an unexpected exception and show a friendly message box.
    Returns the generated error_id (useful for tests / future bug-tracker
    linkage).
    """
    error_id = log_error(
        module=module,
        error_type=type(exc).__name__,
        severity="High",
        action=action,
        status="Open",
        message_reference=str(exc),
    )
    messagebox.showerror(
        "Unexpected Error",
        f"Something went wrong. This has been logged as {error_id}.\n"
        "Please contact the system administrator if the problem continues.",
    )
    return error_id
