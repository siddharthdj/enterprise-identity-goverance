\# IAM Governance Workflows



\## 1. Identity Lifecycle Management



The platform implements the Joiner-Mover-Leaver (JML) lifecycle to manage employee identities and access throughout their employment.



\### 1.1 Joiner — Employee Provisioning



\*\*Objective:\*\* Ensure employees receive appropriate access when they join the organization.



Workflow:



1\. Receive employee information.

2\. Validate mandatory employee attributes.

3\. Verify active employment status.

4\. Map the employee's job title to an IAM role.

5\. Create the employee record and digital identity.

6\. Generate a username.

7\. Assign the mapped role.

8\. Record the provisioning event in the audit log.



\*\*Governance principle:\*\* Access should be based on business role requirements rather than arbitrary individual permissions.



\### 1.2 Mover — Role and Department Changes



\*\*Objective:\*\* Ensure access reflects an employee's current responsibilities.



Workflow:



1\. Receive the employee's updated department and job title.

2\. Validate the employee and new role mapping.

3\. Identify existing role assignments.

4\. Revoke existing active role assignments.

5\. Assign the role corresponding to the employee's new job title.

6\. Update employee attributes.

7\. Record the change in the audit log.



\*\*Governance principle:\*\* Access associated with previous responsibilities should not remain active after a role change without justification.



\### 1.3 Leaver — Employee Deprovisioning



\*\*Objective:\*\* Remove access when an employee leaves the organization.



Workflow:



1\. Identify the employee for termination.

2\. Disable the associated digital identity.

3\. Revoke active role assignments.

4\. Update employment status to terminated.

5\. Record the deprovisioning event in the audit log.



\*\*Governance principle:\*\* Access should be removed promptly when the business relationship ends.



\## 2. Role-Based Access Control



The platform uses RBAC to assign access based on job responsibilities.



Workflow:



1\. Employee job title is received.

2\. Job title is matched against `job\_role\_mapping.json`.

3\. The corresponding IAM role is identified.

4\. Role permissions are retrieved through `role\_permissions`.

5\. Role assignment is recorded in `user\_roles`.



This separates business job titles from technical access permissions.



\## 3. Access Certification



\*\*Objective:\*\* Periodically validate whether existing access remains appropriate.



\### 3.1 Review Generation



1\. An administrator specifies a review period.

2\. The system retrieves active employee-role assignments.

3\. A review record is generated for each eligible assignment.

4\. Duplicate reviews for the same identity, role, and period are prevented.



\### 3.2 Review Decisions



Each review starts with a `pending` decision.



The workflow supports:



| Decision | Result |
|---|---|
| Approved | Access remains assigned |
| Revoked | Corresponding role assignment is revoked |



The reviewer identifier and decision timestamp are stored with the review record.



\### 3.3 Review Summary



The platform reports:



\- Total access reviews

\- Approved reviews

\- Revoked reviews

\- Pending reviews



\## 4. Audit Logging and Reporting



Governance operations generate audit events containing:



\- Actor

\- Target identity

\- Event type

\- Event details

\- Outcome

\- Event timestamp



The audit reporting module retrieves recent events and associates them with employee information where available.



\## 5. Governance Controls Demonstrated



| Governance Area | Implemented Control |
|---|---|
| Identity lifecycle | Provisioning, movement, deprovisioning |
| Access management | Job-role-based assignment |
| Access certification | Periodic access reviews |
| Access remediation | Role revocation |
| Accountability | Actor recorded in audit events |
| Traceability | Centralized audit logging |



\## 6. Current Limitations



\- Reviewer identity is supplied through the CLI and is not independently authenticated.

\- Role assignments are based on configured job-title mappings.

\- The application does not connect to production identity providers.

\- Access review decisions are demonstrated through a simulated governance workflow.

\- No automated notification or escalation mechanism is implemented.
