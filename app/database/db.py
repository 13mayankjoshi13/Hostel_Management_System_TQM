"""
SQLite database layer.

get_connection() returns a connection with foreign keys enabled.
initialize_database() creates all tables if they do not already exist
(idempotent — safe to call every time the app starts).
"""
import sqlite3

from app.config import DATABASE_PATH


def get_connection(db_path: str = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path: str = None) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            registration_number TEXT NOT NULL UNIQUE,
            contact_number TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Allocation and complaint tables are declared now so the schema is
    # stable for the next development batch (Room Allocation module).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            allocated_at TEXT NOT NULL DEFAULT (datetime('now')),
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            assigned_to TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            resolved_at TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            module TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            root_cause TEXT,
            corrective_action TEXT,
            test_case TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'On Leave',
            returned_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            title TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'Hostel Event',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE (event_date, title)
        )
    """)

    # Migration: link a student-role account to its student record.
    existing = {row["name"] for row in cur.execute("PRAGMA table_info(users)")}
    if "student_id" not in existing:
        cur.execute("ALTER TABLE users ADD COLUMN student_id INTEGER REFERENCES students(student_id)")

    if "status" not in existing:
        cur.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'Active'")

    if "failed_attempts" not in existing:
        cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")
    if "locked_until" not in existing:
        cur.execute("ALTER TABLE users ADD COLUMN locked_until TEXT")

    bug_columns = {row["name"] for row in cur.execute("PRAGMA table_info(bugs)")}
    for column in ("reported_by", "fixed_by"):
        if column not in bug_columns:
            cur.execute(f"ALTER TABLE bugs ADD COLUMN {column} TEXT")

    for index_sql in (
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_one_active_room_per_student "
        "ON allocations(student_id) WHERE status = 'Active'",
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_one_open_leave_per_student "
        "ON leaves(student_id) WHERE status = 'On Leave'",
    ):
        try:
            cur.execute(index_sql)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
