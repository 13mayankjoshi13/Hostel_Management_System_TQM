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
CURRENT_USER = "system_admin"   # placeholder until authentication module exists
CURRENT_ROLE = "Administrator"  # placeholder until authentication module exists
