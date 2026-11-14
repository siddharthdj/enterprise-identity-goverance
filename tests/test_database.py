from src.database import get_connection


def test_database_tables_exist(test_db):

    with get_connection() as connection:
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
        "audit_logs",
        "access_reviews"
    }

    assert expected_tables.issubset(tables)