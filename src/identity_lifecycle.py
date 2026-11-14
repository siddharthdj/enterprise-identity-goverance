
import csv
import json
import re
from pathlib import Path

from src.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_config(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_username(full_name, employee_id):
    """Generate a unique, deterministic username."""

    name = re.sub(r"[^a-zA-Z0-9]+", ".", full_name.lower())
    name = name.strip(".")

    return f"{name}.{employee_id.lower()}"


def provision_employee(employee):
    """Provision a new employee identity and assign RBAC access."""

    required_fields = [
        "employee_id",
        "full_name",
        "department",
        "job_title",
        "employment_status"
    ]

    for field in required_fields:
        if not employee.get(field, "").strip():
            raise ValueError(f"Missing required field: {field}")

    if employee["employment_status"].lower() != "active":
        raise ValueError("Only active employees can be provisioned")

    role_mapping = load_config("job_role_mapping.json")
    roles_config = load_config("roles.json")

    job_title = employee["job_title"]
    role_name = role_mapping.get(job_title)

    if not role_name:
        raise ValueError(f"No IAM role mapped for {job_title}")

    role_details = roles_config.get(role_name)

    if not role_details:
        raise ValueError(f"IAM role does not exist: {role_name}")

    if role_details["department"] != employee["department"]:
        raise ValueError("Department and IAM role mismatch")

    username = generate_username(
        employee["full_name"],
        employee["employee_id"]
    )

    connection = get_connection()

    try:
        with connection:
            cursor = connection.cursor()

            # Check for an existing employee
            existing = cursor.execute("""
                SELECT employee_id FROM employees
                WHERE employee_id = ?
            """, (employee["employee_id"],)).fetchone()

            if existing:
                raise ValueError("Employee already exists")

            # Create employee record
            cursor.execute("""
                INSERT INTO employees (
                    employee_id,
                    full_name,
                    department,
                    job_title,
                    employment_status
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                employee["employee_id"],
                employee["full_name"],
                employee["department"],
                employee["job_title"],
                "active"
            ))

            # Create digital identity
            cursor.execute("""
                INSERT INTO identities (
                    employee_id,
                    username,
                    account_status
                )
                VALUES (?, ?, ?)
            """, (
                employee["employee_id"],
                username,
                "enabled"
            ))

            identity_id = cursor.lastrowid

            # Find the IAM role
            role = cursor.execute("""
                SELECT role_id FROM roles
                WHERE role_name = ?
            """, (role_name,)).fetchone()

            if not role:
                raise ValueError(
                    "Role not found. Run seed_data.py first."
                )

            # Assign role
            cursor.execute("""
                INSERT INTO user_roles (
                    identity_id,
                    role_id,
                    assigned_by
                )
                VALUES (?, ?, ?)
            """, (
                identity_id,
                role["role_id"],
                "IAM_AUTOMATION"
            ))

            # Record audit event
            cursor.execute("""
                INSERT INTO audit_logs (
                    actor,
                    target_identity_id,
                    event_type,
                    event_details,
                    outcome
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                "IAM_AUTOMATION",
                identity_id,
                "IDENTITY_PROVISIONED",
                json.dumps({
                    "employee_id": employee["employee_id"],
                    "username": username,
                    "assigned_role": role_name
                }),
                "success"
            ))

        print(
            f"SUCCESS: {employee['employee_id']} "
            f"provisioned as {username} with role {role_name}"
        )

        return username

    finally:
        connection.close()

def move_employee(employee_id, new_department, new_job_title, actor="HR_ADMIN"):
    """
    Transfer an employee to a new department or job role.
    Revoke old access and assign the new role.
    """

    mapping = load_config(DATA_DIR / "job_role_mapping.json")
    roles_config = load_config(DATA_DIR / "roles.json")

    if new_job_title not in mapping:
        raise ValueError(f"No role mapping found for {new_job_title}")

    role_name = mapping[new_job_title]

    if role_name not in roles_config:
        raise ValueError(f"Role configuration not found: {role_name}")

    if roles_config[role_name]["department"] != new_department:
        raise ValueError("New role does not belong to the specified department")

    with get_connection() as conn:

        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not employee:
            raise ValueError(f"Employee not found: {employee_id}")

        if employee["employment_status"] != "active":
            raise ValueError("Cannot move an inactive employee")

        if (
        employee["department"] == new_department
        and employee["job_title"] == new_job_title
        ):
            raise ValueError("Employee already has this department and job title")

        identity = conn.execute(
            "SELECT * FROM identities WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not identity or identity["account_status"] != "enabled":
            raise ValueError("Employee identity is not enabled")

        new_role = conn.execute(
            "SELECT role_id FROM roles WHERE role_name = ?",
            (role_name,)
        ).fetchone()

        if not new_role:
            raise ValueError(f"Role not found in database: {role_name}")

        # Revoke existing active role assignments
        conn.execute(
            """
            UPDATE user_roles
            SET assignment_status = 'revoked'
            WHERE identity_id = ?
            AND assignment_status = 'active'
            """,
            (identity["identity_id"],)
        )

        # Assign the new role
        conn.execute(
            """
            INSERT INTO user_roles
            (identity_id, role_id, assignment_status, assigned_by)
            VALUES (?, ?, 'active', ?)
            """,
            (identity["identity_id"], new_role["role_id"], actor)
        )

        # Update employee information
        conn.execute(
            """
            UPDATE employees
            SET department = ?, job_title = ?
            WHERE employee_id = ?
            """,
            (new_department, new_job_title, employee_id)
        )

        # Record audit event
        conn.execute(
            """
            INSERT INTO audit_logs
            (actor, target_identity_id, event_type, event_details, outcome)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                actor,
                identity["identity_id"],
                "EMPLOYEE_MOVED",
                f"Employee moved to {new_department} as {new_job_title}",
                "success"
            )
        )

    print(f"SUCCESS: {employee_id} moved to {new_department} - {new_job_title}")


def deprovision_employee(employee_id, actor="IAM_AUTOMATION"):
    """Disable an employee identity and revoke all active access."""

    with get_connection() as conn:

        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not employee:
            raise ValueError(f"Employee not found: {employee_id}")

        if employee["employment_status"] != "active":
            raise ValueError("Employee is already inactive or terminated")

        identity = conn.execute(
            "SELECT * FROM identities WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not identity:
            raise ValueError("Employee identity not found")

        # Disable digital identity
        conn.execute(
            """
            UPDATE identities
            SET account_status = 'disabled'
            WHERE employee_id = ?
            """,
            (employee_id,)
        )

        # Revoke all active role assignments
        conn.execute(
            """
            UPDATE user_roles
            SET assignment_status = 'revoked'
            WHERE identity_id = ?
            AND assignment_status = 'active'
            """,
            (identity["identity_id"],)
        )

        # Mark employee as terminated
        conn.execute(
            """
            UPDATE employees
            SET employment_status = 'terminated'
            WHERE employee_id = ?
            """,
            (employee_id,)
        )

        # Record audit event
        conn.execute(
            """
            INSERT INTO audit_logs (
                actor,
                target_identity_id,
                event_type,
                event_details,
                outcome
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                actor,
                identity["identity_id"],
                "IDENTITY_DEPROVISIONED",
                f"Employee {employee_id} terminated and access revoked",
                "success"
            )
        )

    print(f"SUCCESS: {employee_id} deprovisioned. All access revoked.")

def provision_from_csv():
    """Process employee records from the HR CSV feed."""

    with open(
        DATA_DIR / "employees.csv",
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for employee in reader:
            try:
                provision_employee(employee)

            except ValueError as error:
                print(
                    f"REJECTED: {employee.get('employee_id')} "
                    f"- {error}"
                )


if __name__ == "__main__":
    provision_from_csv()
