from datetime import date

from app.models import BankTransaction, Invoice


def test_create_invoice(client, sample_client):
    response = client.post(
        "/api/invoices",
        json={
            "invoice_number": "AF-TEST-001",
            "client_id": sample_client.id,
            "issued_on": "2025-04-01",
            "due_date": "2025-04-15",
            "amount": 1999.5,
            "vat_rate": 0.21,
            "status": "pending",
            "notes": "First invoice from the test",
        },
    )

    payload = response.json()
    assert response.status_code == 201
    assert payload["invoice_number"] == "AF-TEST-001"
    assert payload["amount"] == 1999.5
    assert payload["status"] == "pending"


def test_duplicate_invoice_rejected(client, sample_client):
    payload = {
        "invoice_number": "AF-DUP-001",
        "client_id": sample_client.id,
        "issued_on": "2025-04-01",
        "due_date": "2025-04-20",
        "amount": 800,
        "vat_rate": 0.21,
        "status": "pending",
        "notes": "Duplicate test",
    }

    first = client.post("/api/invoices", json=payload)
    second = client.post("/api/invoices", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_reconciliation_clean_match(client, clean_match_data):
    invoice, transaction = clean_match_data

    response = client.get("/api/reconciliation/suggestions")

    assert response.status_code == 200
    suggestion = next(item for item in response.json() if item["transaction_id"] == transaction.id)
    assert suggestion["status"] == "clean_match"
    assert suggestion["candidate_invoice_ids"] == [invoice.id]


def test_reconciliation_ambiguous_match(client, db_session, seeded_invoice_pair):
    invoice_one, invoice_two = seeded_invoice_pair
    transaction = BankTransaction(
        transaction_ref="TX-AMB-001",
        booked_on=date(2025, 2, 23),
        amount=1200,
        counterparty="Manual review case",
        reference_text="same amount twice",
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    response = client.get("/api/reconciliation/suggestions")

    assert response.status_code == 200
    suggestion = next(item for item in response.json() if item["transaction_id"] == transaction.id)
    assert suggestion["status"] == "manual_review"
    assert set(suggestion["candidate_invoice_ids"]) == {invoice_one.id, invoice_two.id}


def test_reconciliation_apply_marks_paid(client, db_session, clean_match_data):
    invoice, transaction = clean_match_data
    client.get("/api/reconciliation/suggestions")

    response = client.post(
        "/api/reconciliation/apply",
        json={"transaction_id": transaction.id, "invoice_id": invoice.id},
    )

    db_session.refresh(invoice)
    db_session.refresh(transaction)

    assert response.status_code == 200
    assert invoice.status == "paid"
    assert transaction.reconciled is True


def test_dashboard_metrics_shape(client, db_session, sample_client):
    db_session.add(
        Invoice(
            invoice_number="DASH-001",
            client_id=sample_client.id,
            issued_on=date(2025, 4, 1),
            due_date=date(2025, 4, 10),
            amount=950,
            vat_rate=0.21,
            status="collectible",
        )
    )
    db_session.commit()

    response = client.get("/api/dashboard")

    payload = response.json()
    assert response.status_code == 200
    expected_keys = {
        "revenue_invoiced",
        "expenses_total",
        "collectibles_total",
        "due_soon_invoices",
        "review_queue",
        "vat_estimate",
        "cash_flow",
        "invoice_count",
        "expense_count",
        "transaction_count",
    }
    assert expected_keys.issubset(payload.keys())


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
