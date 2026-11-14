
from src.database import get_connection


def get_audit_logs(limit=50):
    """Retrieve recent IAM audit events."""

    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    connection = get_connection()

    try:
        logs = connection.execute("""
            SELECT
                al.audit_id,
                al.actor,
                al.event_type,
                al.outcome,
                al.event_details,
                al.event_timestamp,
                e.employee_id,
                e.full_name,
                e.department
            FROM audit_logs al
            LEFT JOIN identities i
                ON al.target_identity_id = i.identity_id
            LEFT JOIN employees e
                ON i.employee_id = e.employee_id
            ORDER BY al.audit_id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(log) for log in logs]

    finally:
        connection.close()
