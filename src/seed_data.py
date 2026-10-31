
import json
from pathlib import Path

from src.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    """Read a JSON configuration file."""
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def seed_roles_and_permissions():
    roles = load_json("roles.json")
    permissions = load_json("permissions.json")

    connection = get_connection()

    try:
        with connection:
            cursor = connection.cursor()

            for role_name, details in roles.items():

                # Create role if it doesn't already exist
                cursor.execute("""
                    INSERT OR IGNORE INTO roles
                    (role_name, description)
                    VALUES (?, ?)
                """, (role_name, details["description"]))

                cursor.execute("""
                    SELECT role_id FROM roles
                    WHERE role_name = ?
                """, (role_name,))

                role_id = cursor.fetchone()["role_id"]

                # Create permissions and associate them with the role
                for permission in permissions.get(role_name, []):

                    cursor.execute("""
                        INSERT OR IGNORE INTO permissions
                        (application, resource, action)
                        VALUES (?, ?, ?)
                    """, (
                        permission["application"],
                        permission["resource"],
                        permission["action"]
                    ))

                    cursor.execute("""
                        SELECT permission_id
                        FROM permissions
                        WHERE application = ?
                        AND resource = ?
                        AND action = ?
                    """, (
                        permission["application"],
                        permission["resource"],
                        permission["action"]
                    ))

                    permission_id = cursor.fetchone()["permission_id"]

                    cursor.execute("""
                        INSERT OR IGNORE INTO role_permissions
                        (role_id, permission_id)
                        VALUES (?, ?)
                    """, (role_id, permission_id))

        print("RBAC configuration loaded successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    seed_roles_and_permissions()
