
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
