from src.database import get_connection


def test_rbac_configuration_loaded(test_db):

    with get_connection() as connection:

        roles = connection.execute(
            "SELECT COUNT(*) FROM roles"
        ).fetchone()[0]

        permissions = connection.execute(
            "SELECT COUNT(*) FROM permissions"
        ).fetchone()[0]

        mappings = connection.execute(
            "SELECT COUNT(*) FROM role_permissions"
        ).fetchone()[0]

    assert roles == 5
    assert permissions == 10
    assert mappings == 10