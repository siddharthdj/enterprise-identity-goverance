# Enterprise Identity Governance Platform

A Python-based Identity and Access Management (IAM) platform demonstrating identity lifecycle management, Role-Based Access Control (RBAC), access certification, and audit reporting.

## Overview

This project simulates enterprise IAM governance for a fictional organization. It provides a centralized workflow for managing employee identities, assigning role-based access, reviewing access entitlements, and maintaining audit records.

## Key Capabilities

- **Identity Lifecycle Management:** Supports employee provisioning, role changes, and deprovisioning.
- **Role-Based Access Control (RBAC):** Maps job roles to permissions and automates access assignments.
- **Access Certification:** Generates periodic access reviews and supports approval and revocation decisions.
- **Audit Logging:** Records identity and access governance activities with actor, event type, outcome, and timestamp.
- **Audit Reporting:** Retrieves and displays recent IAM events.
- **CLI Interface:** Provides an interactive interface for executing governance workflows.

## Technology Stack

- Python
- SQLite
- JSON and CSV
- Pytest

## Project Structure

```text
enterprise-identity-goverance/
├── data/
│   ├── employees.csv
│   ├── roles.json
│   ├── permissions.json
│   └── job_role_mapping.json
├── docs/
├── reports/
├── src/
│   ├── access_certification.py
│   ├── audit_reporting.py
│   ├── cli.py
│   ├── database.py
│   ├── identity_lifecycle.py
│   └── seed_data.py
├── tests/
├── README.md
├── requirements.txt
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd enterprise-identity-goverance
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m src.cli
```

### 5. Run tests

```bash
pytest -v
```

## Testing

The project includes automated tests covering database initialization, RBAC configuration, identity lifecycle operations, access certification, and audit reporting.

Current test status: **16 tests passed**.

## Project Scope

This is a hands-on IAM governance implementation intended to demonstrate practical understanding of identity lifecycle processes, access governance, RBAC, and auditability.

It is a portfolio project and does not currently integrate with production identity providers.