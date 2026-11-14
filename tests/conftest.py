import pytest

from src.database import initialize_database
from src.seed_data import seed_roles_and_permissions
from src.identity_lifecycle import provision_employee


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a fresh IAM database for each test."""

    test_database = tmp_path / "iam.db"

    # Redirect database connections to the temporary database
    monkeypatch.setattr(
        "src.database.DATABASE_PATH",
        test_database
    )

    # Initialize schema and seed RBAC configuration
    initialize_database(test_database)
    seed_roles_and_permissions()

    # Create a baseline employee for lifecycle tests
    provision_employee({
        "employee_id": "EMP001",
        "full_name": "John Smith",
        "department": "Finance",
        "job_title": "Finance Analyst",
        "employment_status": "active"
    })

    return test_database