
import sqlite3
from pathlib import Path

# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database will be created inside data/
DATABASE_PATH = BASE_DIR / "data" / "iam.db"


def get_connection():
    """Create a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)

    # Return database rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    # Enforce foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create the IAM database tables."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                job_title TEXT NOT NULL,
                employment_status TEXT NOT NULL
                    CHECK (employment_status IN
                    ('active', 'inactive', 'terminated')),
                created_at TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            );

            CREATE TABLE IF NOT EXISTS identities (
                identity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                account_status TEXT NOT NULL
                    CHECK (account_status IN
                    ('enabled', 'disabled', 'locked')),
                created_at TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY (employee_id)
                    REFERENCES employees(employee_id)
            );

            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT NOT NULL UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                application TEXT NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                UNIQUE(application, resource, action)
            );

            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id)
                    REFERENCES roles(role_id),
                FOREIGN KEY (permission_id)
                    REFERENCES permissions(permission_id)
            );

            CREATE TABLE IF NOT EXISTS user_roles (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                identity_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                assignment_status TEXT NOT NULL DEFAULT 'active'
                    CHECK (assignment_status IN
                    ('active', 'revoked')),
                assigned_by TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY (identity_id)
                    REFERENCES identities(identity_id),
                FOREIGN KEY (role_id)
                    REFERENCES roles(role_id)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                target_identity_id INTEGER,
                event_type TEXT NOT NULL,
                event_details TEXT,
                outcome TEXT NOT NULL
                    CHECK (outcome IN
                    ('success', 'failure')),
                event_timestamp TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY (target_identity_id)
                    REFERENCES identities(identity_id)
            );
        """)

        connection.commit()
        print("IAM database initialized successfully!")

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
