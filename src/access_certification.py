from src.database import get_connection


def generate_access_review(review_period):
    """Generate access review records for all active employee role assignments."""

    connection = get_connection()

    try:
        with connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    i.identity_id,
                    ur.role_id
                FROM identities i
                JOIN employees e
                    ON i.employee_id = e.employee_id
                JOIN user_roles ur
                    ON i.identity_id = ur.identity_id
                WHERE e.employment_status = 'active'
                AND i.account_status = 'enabled'
                AND ur.assignment_status = 'active'
            """)

            assignments = cursor.fetchall()

            for assignment in assignments:
                cursor.execute("""
                    INSERT OR IGNORE INTO access_reviews (
                        identity_id,
                        role_id,
                        review_period
                    )
                    VALUES (?, ?, ?)
                """, (
                    assignment["identity_id"],
                    assignment["role_id"],
                    review_period
                ))

        print(
            f"Access review generated for {review_period}. "
            f"Found {len(assignments)} active assignments."
        )

    finally:
        connection.close()


def review_access(review_id, decision, reviewer):
    """Approve or revoke an employee's role assignment."""

    if decision not in ("approved", "revoked"):
        raise ValueError("Decision must be 'approved' or 'revoked'.")

    if not reviewer or not reviewer.strip():
        raise ValueError("Reviewer cannot be empty.")

    connection = get_connection()

    try:
        with connection:
            cursor = connection.cursor()

            # Find the review record
            review = cursor.execute("""
                SELECT *
                FROM access_reviews
                WHERE review_id = ?
            """, (review_id,)).fetchone()

            if review is None:
                raise ValueError("Access review record not found.")

            if review["decision"] != "pending":
                raise ValueError("This access review has already been completed.")

            # Update the review decision
            cursor.execute("""
                UPDATE access_reviews
                SET decision = ?,
                    reviewer = ?,
                    review_timestamp = CURRENT_TIMESTAMP
                WHERE review_id = ?
            """, (decision, reviewer, review_id))

            # Revoke the actual role assignment if required
            if decision == "revoked":
                cursor.execute("""
                    UPDATE user_roles
                    SET assignment_status = 'revoked'
                    WHERE identity_id = ?
                    AND role_id = ?
                    AND assignment_status = 'active'
                """, (
                    review["identity_id"],
                    review["role_id"]
                ))

                if cursor.rowcount == 0:
                    raise ValueError("No active role assignment found to revoke.")

            # Record the decision in the audit log
            cursor.execute("""
                INSERT INTO audit_logs (
                        target_identity_id,
                        event_type,
                        actor,
                        outcome,
                        event_details
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                review["identity_id"],
                "ACCESS_REVIEW_" + decision.upper(),
                reviewer,
                "success",
                f"Access review {review_id}: {decision}"
            ))

        print(
            f"Access review {review_id} "
            f"successfully marked as {decision}."
        )

    finally:
        connection.close()


def get_access_review_summary(review_period):
    """Return access certification statistics for a review period."""

    connection = get_connection()

    try:
        summary = connection.execute("""
            SELECT
                COUNT(*) AS total_reviews,
                COALESCE(SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END), 0) AS approved,
                COALESCE(SUM(CASE WHEN decision = 'revoked' THEN 1 ELSE 0 END), 0) AS revoked,
                COALESCE(SUM(CASE WHEN decision = 'pending' THEN 1 ELSE 0 END), 0) AS pending
            FROM access_reviews
            WHERE review_period = ?
            """, (review_period,)).fetchone()

        return {
            "total_reviews": summary["total_reviews"],
            "approved": summary["approved"],
            "revoked": summary["revoked"],
            "pending": summary["pending"]
        }

    finally:
        connection.close()

def get_pending_access_reviews(review_period):
    """Return all pending access reviews for a given period."""
    connection = get_connection()
    try:
        reviews = connection.execute("""
            SELECT
                ar.review_id,
                ar.review_period,
                ar.decision,
                i.employee_id,
                e.full_name,
                e.department,
                r.role_name
            FROM access_reviews ar
            JOIN identities i ON ar.identity_id = i.identity_id
            JOIN employees e ON i.employee_id = e.employee_id
            JOIN roles r ON ar.role_id = r.role_id
            WHERE ar.review_period = ?
            AND ar.decision = 'pending'
            ORDER BY e.full_name
        """, (review_period,)).fetchall()

        return [dict(review) for review in reviews]
    finally:
        connection.close()


def get_pending_review_by_id(review_period, review_id):
    """Retrieve a pending review by its ID."""
    connection = get_connection()
    try:
        review = connection.execute("""
            SELECT
                ar.review_id,
                ar.review_period,
                ar.decision,
                i.employee_id,
                e.full_name,
                e.department,
                r.role_name
            FROM access_reviews ar
            JOIN identities i ON ar.identity_id = i.identity_id
            JOIN employees e ON i.employee_id = e.employee_id
            JOIN roles r ON ar.role_id = r.role_id
            WHERE ar.review_period = ?
            AND ar.review_id = ?
            AND ar.decision = 'pending'
        """, (review_period, review_id)).fetchone()

        return dict(review) if review else None
    finally:
        connection.close()