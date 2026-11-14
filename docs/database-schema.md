\# Database Schema



\## 1. Overview



The application uses SQLite as its relational database. The schema supports employee records, digital identities, role-based access assignments, access certification, and audit logging.



\## 2. Database Tables



\### employees



Stores employee and organizational information.



| Column | Type | Description |

|---|---|---|

| employee\_id | TEXT | Unique employee identifier |

| full\_name | TEXT | Employee name |

| department | TEXT | Organizational department |

| job\_title | TEXT | Employee's job title |

| employment\_status | TEXT | Employment status |

| created\_at | TEXT | Record creation timestamp |



\### identities



Stores digital identities associated with employees.



| Column | Type | Description |

|---|---|---|

| identity\_id | INTEGER | Identity identifier |

| employee\_id | TEXT | Associated employee |

| username | TEXT | Generated username |

| account\_status | TEXT | Account status |

| created\_at | TEXT | Record creation timestamp |



\### roles



Defines organizational access roles.



| Column | Type | Description |

|---|---|---|

| role\_id | INTEGER | Role identifier |

| role\_name | TEXT | Role name |

| description | TEXT | Role description |



\### permissions



Defines application-level permissions.



| Column | Type | Description |

|---|---|---|

| permission\_id | INTEGER | Permission identifier |

| application | TEXT | Target application |

| resource | TEXT | Resource being accessed |

| action | TEXT | Permitted action |



\### role\_permissions



Implements the many-to-many relationship between roles and permissions.



| Column | Type | Description |

|---|---|---|

| role\_id | INTEGER | Associated role |

| permission\_id | INTEGER | Associated permission |



\### user\_roles



Tracks role assignments to digital identities.



| Column | Type | Description |

|---|---|---|

| assignment\_id | INTEGER | Assignment identifier |

| identity\_id | INTEGER | Associated identity |

| role\_id | INTEGER | Assigned role |

| assignment\_status | TEXT | Assignment status |

| assigned\_by | TEXT | Assignment actor |

| assigned\_at | TEXT | Assignment timestamp |



\### access\_reviews



Stores periodic access certification records.



| Column | Type | Description |

|---|---|---|

| review\_id | INTEGER | Review identifier |

| identity\_id | INTEGER | Identity under review |

| role\_id | INTEGER | Role under review |

| review\_period | TEXT | Certification period |

| reviewer | TEXT | Reviewer identifier |

| decision | TEXT | Pending, approved, or revoked |

| review\_timestamp | DATETIME | Decision timestamp |



\### audit\_logs



Maintains a record of IAM governance events.



| Column | Type | Description |

|---|---|---|

| audit\_id | INTEGER | Audit event identifier |

| actor | TEXT | Actor responsible for the event |

| target\_identity\_id | INTEGER | Affected identity |

| event\_type | TEXT | Type of IAM event |

| event\_details | TEXT | Event description |

| outcome | TEXT | Event outcome |

| event\_timestamp | TEXT | Event timestamp |



\## 3. Entity Relationships



\- One employee can be associated with a digital identity.

\- One identity can have multiple role assignments.

\- One role can be assigned to multiple identities.

\- Roles can contain multiple permissions.

\- Permissions can belong to multiple roles.

\- Access reviews reference an identity and the role being reviewed.

\- Audit events can reference the identity affected by an operation.



\## 4. Access Governance Data Flow



1\. Employee records are used to provision identities.

2\. Job-role mappings determine the appropriate IAM role.

3\. Role-permission mappings define the permissions associated with each role.

4\. User-role assignments track access granted to identities.

5\. Access reviews evaluate existing assignments.

6\. Approval and revocation decisions update governance records.

7\. Audit logs retain a history of relevant operations.



\## 5. Design Considerations



\- Relational tables separate employee, identity, role, and permission data.

\- Foreign keys maintain referential integrity.

\- Access-review records prevent duplicate reviews for the same identity, role, and review period.

\- Audit records provide traceability for governance activities.



The schema is designed for a learning and portfolio implementation and is not intended to represent a production-ready enterprise IAM database.
