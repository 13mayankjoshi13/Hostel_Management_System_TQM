"""
Central configuration for paths used across the application.

Keeping all paths in one place means every module (database, logging,
audit) writes to the same, correct location regardless of which
directory Python was launched from.
"""
import os

# Project root = two levels up from this file (app/config.py -> app -> root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application database
DATABASE_DIR = os.path.join(PROJECT_ROOT, "app", "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "hostel.db")

# TQM quality evidence (Q09: Error Logs, Bug Tracker, Audit Logs, etc.)
TQM_DATA_DIR = os.path.join(PROJECT_ROOT, "TQM", "data")
ERROR_LOG_CSV = os.path.join(TQM_DATA_DIR, "error_logs.csv")
AUDIT_LOG_CSV = os.path.join(TQM_DATA_DIR, "audit_logs.csv")
DEFECT_LOG_CSV = os.path.join(TQM_DATA_DIR, "defect_log.csv")

APP_NAME = "Hostel Management System"
# Fallback values only — used by app.utils.session when nobody is
# logged in (e.g. a service called directly from a script or test).
# The actual logged-in user/role during normal app use comes from
# app.utils.session, set at login by app.services.auth_service.
CURRENT_USER = "system_admin"
CURRENT_ROLE = "Administrator"
