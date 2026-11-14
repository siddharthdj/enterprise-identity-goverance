from src.audit_reporting import get_audit_logs
from src.identity_lifecycle import provision_employee
import pytest


def test_get_audit_logs_rejects_invalid_limit():
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        get_audit_logs(limit=0)


def test_get_audit_logs_rejects_negative_limit():
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        get_audit_logs(limit=-1)

def test_get_audit_logs_rejects_non_integer_limit():
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        get_audit_logs(limit="ten")


def test_get_audit_logs(test_db):
    # Provision an employee to generate an audit event
    provision_employee({
        "employee_id": "EMP002",
        "full_name": "Jane Doe",
        "department": "Engineering",
        "job_title": "Software Developer",
        "employment_status": "active"
    })

    logs = get_audit_logs()

    assert len(logs) >= 1
    assert logs[0]["employee_id"] == "EMP002"
    assert logs[0]["full_name"] == "Jane Doe"
    assert logs[0]["event_type"] == "IDENTITY_PROVISIONED"

def test_get_audit_logs_respects_limit(test_db):
    provision_employee({
        "employee_id": "EMP002",
        "full_name": "Jane Doe",
        "department": "Engineering",
        "job_title": "Software Developer",
        "employment_status": "active"
    })

    provision_employee({
        "employee_id": "EMP003",
        "full_name": "Robert Brown",
        "department": "Finance",
        "job_title": "Finance Analyst",
        "employment_status": "active"
    })

    logs = get_audit_logs(limit=1)

    assert len(logs) == 1
    assert logs[0]["employee_id"] == "EMP003"