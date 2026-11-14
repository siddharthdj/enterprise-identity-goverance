from src.database import get_connection
from src.access_certification import generate_access_review
from src.access_certification import get_access_review_summary
from src.identity_lifecycle import provision_employee
from src.access_certification import (
    generate_access_review,
    review_access,
    get_pending_access_reviews
)
import pytest

from src.access_certification import (
    generate_access_review,
    review_access
)


def test_generate_access_review(test_db):
    review_period = "2026-Q4"

    # Generate the quarterly review
    generate_access_review(review_period)

    with get_connection() as connection:
        reviews = connection.execute("""
            SELECT *
            FROM access_reviews
            WHERE review_period = ?
        """, (review_period,)).fetchall()

        assert len(reviews) == 1
        assert reviews[0]["decision"] == "pending"

    # Run it again to verify duplicate prevention
    generate_access_review(review_period)

    with get_connection() as connection:
        reviews = connection.execute("""
            SELECT *
            FROM access_reviews
            WHERE review_period = ?
        """, (review_period,)).fetchall()

        assert len(reviews) == 1

def test_approve_access(test_db):

    generate_access_review("2026-Q4")

    with get_connection() as connection:
        review = connection.execute("""
            SELECT review_id, identity_id, role_id
            FROM access_reviews
            WHERE review_period = '2026-Q4'
        """).fetchone()

    review_access(
        review_id=review["review_id"],
        decision="approved",
        reviewer="MANAGER001"
    )

    with get_connection() as connection:
        updated_review = connection.execute("""
            SELECT decision, reviewer
            FROM access_reviews
            WHERE review_id = ?
        """, (review["review_id"],)).fetchone()

        assert updated_review["decision"] == "approved"
        assert updated_review["reviewer"] == "MANAGER001"

        role = connection.execute("""
            SELECT assignment_status
            FROM user_roles
            WHERE identity_id = ? AND role_id = ?
        """, (review["identity_id"], review["role_id"])).fetchone()

        assert role["assignment_status"] == "active"

def test_revoke_access(test_db):
    generate_access_review("2026-Q4")

    with get_connection() as connection:
        review = connection.execute("""
            SELECT review_id, identity_id, role_id
            FROM access_reviews
            WHERE review_period = '2026-Q4'
        """).fetchone()

    review_access(
        review_id=review["review_id"],
        decision="revoked",
        reviewer="MANAGER001"
    )

    with get_connection() as connection:
        updated_review = connection.execute("""
            SELECT decision
            FROM access_reviews
            WHERE review_id = ?
        """, (review["review_id"],)).fetchone()

        assert updated_review["decision"] == "revoked"

        role = connection.execute("""
            SELECT assignment_status
            FROM user_roles
            WHERE identity_id = ? AND role_id = ?
        """, (review["identity_id"], review["role_id"])).fetchone()

        assert role["assignment_status"] == "revoked"

def test_prevent_repeated_review_decision(test_db):

    generate_access_review("2026-Q4")

    with get_connection() as connection:
        review = connection.execute("""
            SELECT review_id
            FROM access_reviews
            WHERE review_period = '2026-Q4'
        """).fetchone()

    review_access(
        review_id=review["review_id"],
        decision="approved",
        reviewer="MANAGER001"
    )

    with pytest.raises(ValueError):
        review_access(
            review_id=review["review_id"],
            decision="revoked",
            reviewer="MANAGER002"
        )

def test_access_review_summary(test_db):
    generate_access_review("2026-Q4")

    with get_connection() as connection:
        review = connection.execute("""
            SELECT review_id
            FROM access_reviews
            WHERE review_period = '2026-Q4'
        """).fetchone()

    review_access(
        review_id=review["review_id"],
        decision="approved",
        reviewer="MANAGER001"
    )

    summary = get_access_review_summary("2026-Q4")

    assert summary["total_reviews"] == 1
    assert summary["approved"] == 1
    assert summary["revoked"] == 0
    assert summary["pending"] == 0

def test_get_pending_access_reviews(test_db):
    # Create a second employee
    provision_employee({
        "employee_id": "EMP002",
        "full_name": "Jane Doe",
        "department": "Engineering",
        "job_title": "Software Developer",
        "employment_status": "active"
    })

    # Generate quarterly reviews for both employees
    generate_access_review("2026-Q4")

    # Retrieve EMP001's review
    with get_connection() as connection:
        review = connection.execute("""
            SELECT review_id
            FROM access_reviews ar
            JOIN identities i
                ON ar.identity_id = i.identity_id
            WHERE i.employee_id = 'EMP001'
            AND ar.review_period = '2026-Q4'
        """).fetchone()

    # Approve EMP001's access
    review_access(
        review_id=review["review_id"],
        decision="approved",
        reviewer="MANAGER001"
    )

    # Retrieve pending reviews
    pending = get_pending_access_reviews("2026-Q4")

    assert len(pending) == 1
    assert pending[0]["employee_id"] == "EMP002"
    assert pending[0]["full_name"] == "Jane Doe"
    assert pending[0]["decision"] == "pending"

def test_access_review_summary_empty_period(test_db):
    summary = get_access_review_summary("2027-Q1")

    assert summary == {
        "total_reviews": 0,
        "approved": 0,
        "revoked": 0,
        "pending": 0
    }