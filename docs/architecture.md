\# System Architecture



\## 1. Overview



The Enterprise Identity Governance Platform is a Python-based application designed to simulate core enterprise Identity and Access Management (IAM) processes.



The system uses a modular architecture to separate identity lifecycle operations, access governance, database management, and audit reporting.



\## 2. Architecture



```text

&#x20;               HR Employee Data

&#x20;                (employees.csv)

&#x20;                      |

&#x20;                      v

&#x20;             Identity Lifecycle

&#x20;             Provision / Move /

&#x20;                Deprovision

&#x20;                      |

&#x20;                      v

&#x20;               RBAC Engine

&#x20;            Job Role -> IAM Role

&#x20;                      |

&#x20;                      v

&#x20;               SQLite Database

&#x20;                      |

&#x20;         +------------+------------+

&#x20;         |            |            |

&#x20;         v            v            v

&#x20;    Access         Audit       Identity

&#x20; Certification   Reporting    Records

&#x20;         |            |

&#x20;         v            v

&#x20;    Approve /      Audit Logs

&#x20;     Revoke

&#x20;         |

&#x20;         v

&#x20;      CLI Interface

```



\## 3. Application Components



| Component | Responsibility |
|---|---|
| `database.py` | Database connection and schema initialization |
| `seed\_data.py` | Loads roles, permissions, and role-permission mappings |
| `identity\_lifecycle.py` | Employee provisioning, transfers, and deprovisioning |
| `access\_certification.py` | Periodic access reviews and approval/revocation workflows |
| `audit\_reporting.py` | Retrieves and reports IAM audit events |
| `cli.py` | Interactive interface for IAM operations |



\## 4. Data Architecture



The application uses SQLite to maintain identity and access governance records.



Core database entities:



\- \*\*employees:\*\* Employee information and employment status.

\- \*\*identities:\*\* Digital identity records associated with employees.

\- \*\*roles:\*\* Business and technical access roles.

\- \*\*permissions:\*\* Individual access permissions.

\- \*\*role\_permissions:\*\* Maps permissions to roles.

\- \*\*user\_roles:\*\* Tracks role assignments and their status.

\- \*\*access\_reviews:\*\* Stores periodic access certification decisions.

\- \*\*audit\_logs:\*\* Records governance activities and outcomes.



\## 5. Identity Lifecycle Workflow



\### Joiner

1\. Employee data is received.

2\. Employment status and required attributes are validated.

3\. A digital identity is created.

4\. The employee's job title is mapped to an IAM role.

5\. Role assignments are recorded.

6\. The provisioning activity is logged.



\### Mover

1\. Employee department and job title are updated.

2\. Existing role assignments are revoked.

3\. The new job title is mapped to the appropriate IAM role.

4\. The new role is assigned.

5\. The transfer is recorded in the audit log.



\### Leaver

1\. The employee is identified for termination.

2\. The digital identity is disabled.

3\. Active role assignments are revoked.

4\. Employment status is updated.

5\. The deprovisioning activity is logged.



\## 6. Access Certification Workflow



1\. An access review is generated for a defined review period.

2\. Active employee-role assignments are included.

3\. Reviews remain pending until a decision is recorded.

4\. An authorized workflow operator approves or revokes access.

5\. Revoked assignments are marked accordingly.

6\. Decisions are recorded in the audit log.



\## 7. Technology Choices



\- \*\*Python:\*\* Implements IAM business logic and workflows.

\- \*\*SQLite:\*\* Provides persistent relational storage.

\- \*\*CSV:\*\* Represents incoming employee data.

\- \*\*JSON:\*\* Stores role, permission, and job-role configuration.

\- \*\*Pytest:\*\* Validates application functionality and expected behavior.



\## 8. Scope and Limitations



This project is a portfolio implementation of IAM governance concepts. It does not currently integrate with production identity providers or implement authenticated reviewer identities.



The CLI currently acts as the operational interface for executing governance workflows.
