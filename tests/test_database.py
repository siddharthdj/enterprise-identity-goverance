
from src.database import (
    initialize_database,
    get_connection
)


def test_database_tables_exist():
    initialize_database()

    connection = get_connection()

    cursor = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = {row["name"] for row in cursor.fetchall()}

    expected_tables = {
        "employees",
        "identities",
        "roles",
        "permissions",
        "role_permissions",
        "user_roles",
        "audit_logs"
    }

    connection.close()

    assert expected_tables.issubset(tables)
