# AdminFlow

[![CI](https://github.com/delbandb/finance-ops-control/actions/workflows/ci.yml/badge.svg)](https://github.com/delbandb/finance-ops-control/actions/workflows/ci.yml)

AdminFlow is a small finance-operations backend for tracking invoices, expenses, and bank transactions. The core idea is simple: keep admin data structured, expose it through a clean API, and add reconciliation logic so incoming payments can be matched against open invoices without guessing.

## Recruiter Quick Scan

- Built a FastAPI backend with SQLAlchemy models, Pydantic schemas, repository helpers, and service-layer reconciliation logic.
- Added tests for API creation flows, duplicate protection, clean matches, ambiguous matches, apply behavior, dashboard metrics, and health checks.
- Included Docker, Docker Compose, environment configuration, seed data, architecture notes, and deployment notes.
- Designed conservative finance logic that sends ambiguous payment matches to manual review instead of applying risky automation.

## Why I Built It

I wanted a backend project based on a workflow I understand from an admin and finance perspective. In real operations work, the difficult part is rarely just storing invoices. It is knowing which invoices are still open, which payments close them, which transactions need manual review, and what the current cash position looks like.

AdminFlow focuses on that practical workflow instead of being a generic CRUD demo.

## What It Does

- Stores clients, invoices, expenses, and bank transactions.
- Exposes a FastAPI REST API for the main finance entities.
- Builds dashboard metrics for revenue, expenses, collectibles, VAT estimate, review queue, and cash flow.
- Suggests reconciliation matches between unreconciled bank transactions and open invoices.
- Flags ambiguous matches for manual review instead of applying the wrong invoice.
- Includes a small HTML dashboard for a quick browser view.
- Includes tests for API flows, duplicate protection, reconciliation, and dashboard shape.
- Can run locally or through Docker Compose.

## Reconciliation Logic

The reconciliation engine is intentionally conservative:

- It only considers invoices with an open status such as `pending` or `collectible`.
- It compares transaction amount and invoice amount within a small tolerance.
- If exactly one invoice matches, it returns a clean match.
- If more than one invoice matches, it marks the transaction for manual review.
- If no invoice matches, it leaves the transaction unmatched.
- Applying a suggestion marks the invoice as paid and the transaction as reconciled together.

That design avoids pretending the system knows more than it does. In finance tools, a safe review queue is better than a confident wrong match.

## Tech Stack

| Area | Tools |
| --- | --- |
| Language | Python |
| API | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| UI | Jinja2 templates, static CSS |
| Testing | pytest, httpx |
| Packaging | Docker, Docker Compose |

## API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Browser dashboard |
| GET | `/api/health` | Health check |
| GET | `/api/invoices` | List invoices |
| POST | `/api/invoices` | Create invoice |
| GET | `/api/expenses` | List expenses |
| POST | `/api/expenses` | Create expense |
| GET | `/api/transactions` | List bank transactions |
| POST | `/api/transactions` | Create bank transaction |
| GET | `/api/reconciliation/suggestions` | List reconciliation suggestions |
| POST | `/api/reconciliation/apply` | Apply a clean reconciliation match |
| GET | `/api/dashboard` | Dashboard metrics JSON |

## Project Structure

```text
finance-ops-control/
|-- app/
|   |-- api/routes.py              # API and dashboard routes
|   |-- core/config.py             # App configuration
|   |-- core/database.py           # SQLAlchemy session and engine
|   |-- core/repository.py         # Database access helpers
|   |-- models.py                  # SQLAlchemy models
|   |-- schemas/finance.py         # Pydantic request/response models
|   |-- services/reconciliation.py # Matching and dashboard logic
|   |-- static/style.css           # Dashboard styling
|   |-- templates/dashboard.html   # Built-in HTML dashboard
|   `-- main.py                    # FastAPI app factory
|-- tests/test_api.py              # API and service tests
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Run Locally

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
copy .env.example .env
.venv/Scripts/python -m uvicorn app.main:app --reload
```

Open the app at:

```text
http://127.0.0.1:8000
```

On macOS or Linux, use `source .venv/bin/activate` and `python -m uvicorn app.main:app --reload`.

## Run With Docker

```bash
docker compose up --build
```

## Run Tests

```bash
pytest
```

## Example Requests

Create an invoice:

```bash
curl -X POST http://127.0.0.1:8000/api/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "AF-INV-NEW-001",
    "client_id": 1,
    "issued_on": "2025-07-01",
    "due_date": "2025-07-15",
    "amount": 1800,
    "vat_rate": 0.21,
    "status": "pending",
    "notes": "test invoice from curl"
  }'
```

Get reconciliation suggestions:

```bash
curl http://127.0.0.1:8000/api/reconciliation/suggestions
```

Get dashboard metrics:

```bash
curl http://127.0.0.1:8000/api/dashboard
```

## What I Would Improve Next

- Add JWT authentication and role-based permissions.
- Move from SQLite to PostgreSQL with Alembic migrations.
- Add CSV import for bank statements.
- Add PDF invoice export.
- Add GitHub Actions for automated test runs.
- Expand the dashboard into a richer frontend if the workflow grows.
