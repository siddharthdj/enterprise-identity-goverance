# IAM Governance Platform — Demonstration

This document demonstrates the core IAM governance workflows implemented in the Nexora IAM Governance Platform.

## 1. Access Review Generation

**Review period:** 2027-Q1

Generated access reviews for all active role assignments.

- Total reviews generated: 9
- Duplicate review generation is prevented through database constraints and `INSERT OR IGNORE`.

## 2. Access Certification Decisions

Two access review decisions were processed through the CLI.

| Employee | Role | Decision | Reviewer |
|---|---|---|---|
| Anna White | Security Analyst | Approved | Security_Manager_01 |
| Daniel Martin | IT Administrator | Revoked | Security_Manager_01 |

## 3. Access Review Summary

**Review period:** 2027-Q1

| Metric | Count |
|---|---:|
| Total reviews | 9 |
| Approved | 1 |
| Revoked | 1 |
| Pending | 7 |

## 4. Access Enforcement Verification

The database was queried after processing the decisions to verify the actual role assignment status.

| Employee | Employee ID | Role | Assignment Status |
|---|---|---|---|
| Daniel Martin | EMP009 | IT Administrator | Revoked |
| Anna White | EMP010 | Security Analyst | Active |

The results confirm that revocation updates the underlying role assignment, while approval preserves the existing assignment.

## 5. Audit Trail

The audit reporting module recorded both decisions.

| Audit ID | Employee | Event | Actor | Outcome |
|---|---|---|---|---|
| 16 | Daniel Martin | ACCESS_REVIEW_REVOKED | Security_Manager_01 | Success |
| 15 | Anna White | ACCESS_REVIEW_APPROVED | Security_Manager_01 | Success |

Audit records include the actor, target identity, event type, outcome, event details, and timestamp.

## 6. Scope and Limitations

- Reviewer identity is currently captured as a user-provided identifier; authentication and authorization of reviewers are not implemented.
- Access reviews operate on role assignments within the local SQLite database.
- Integration with enterprise identity providers and IAM platforms is outside this project's scope.

## Demonstrated Capabilities

- Access certification generation
- Approval and revocation workflows
- Role assignment enforcement
- Audit logging and reporting
- Database-level verification of access decisions