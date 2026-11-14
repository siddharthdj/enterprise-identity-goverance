from src.identity_lifecycle import move_employee
from src.identity_lifecycle import deprovision_employee
from src.database import get_connection


def test_move_employee(test_db):
    move_employee(
        employee_id="EMP001",
        new_department="IT",
        new_job_title="IT Administrator"
    )

    with get_connection() as conn:

        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            ("EMP001",)
        ).fetchone()

        assert employee["department"] == "IT"
        assert employee["job_title"] == "IT Administrator"

        active_roles = conn.execute("""
            SELECT r.role_name
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.role_id
            JOIN identities i ON ur.identity_id = i.identity_id
            WHERE i.employee_id = ?
            AND ur.assignment_status = 'active'
        """, ("EMP001",)).fetchall()

        assert len(active_roles) == 1
        assert active_roles[0]["role_name"] == "IT Administrator"

        revoked_roles = conn.execute("""
            SELECT r.role_name
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.role_id
            JOIN identities i ON ur.identity_id = i.identity_id
            WHERE i.employee_id = ?
            AND ur.assignment_status = 'revoked'
        """, ("EMP001",)).fetchall()

        assert any(
            role["role_name"] == "Finance Analyst"
            for role in revoked_roles
        )



def test_deprovision_employee(test_db):

    deprovision_employee("EMP001")

    with get_connection() as conn:

        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            ("EMP001",)
        ).fetchone()

        identity = conn.execute(
            "SELECT * FROM identities WHERE employee_id = ?",
            ("EMP001",)
        ).fetchone()

        active_roles = conn.execute("""
            SELECT * FROM user_roles
            WHERE identity_id = ?
            AND assignment_status = 'active'
        """, (identity["identity_id"],)).fetchall()

        audit = conn.execute("""
            SELECT * FROM audit_logs
            WHERE target_identity_id = ?
            AND event_type = 'IDENTITY_DEPROVISIONED'
        """, (identity["identity_id"],)).fetchone()

        assert employee["employment_status"] == "terminated"
        assert identity["account_status"] == "disabled"
        assert len(active_roles) == 0
        assert audit is not None