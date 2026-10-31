
from src.database import get_connection
from src.seed_data import seed_roles_and_permissions


def test_rbac_configuration_loaded():
    seed_roles_and_permissions()

    connection = get_connection()

    try:
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

    finally:
        connection.close()
