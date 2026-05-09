from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.core.database as db_module
import app.main as main_module
from app.core.database import Base, get_db
from app.main import app
from app.models import BankTransaction, Client, Invoice


@pytest.fixture
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(db_module, "engine", engine)
    monkeypatch.setattr(db_module, "SessionLocal", testing_session_local)
    monkeypatch.setattr(main_module, "engine", engine)
    monkeypatch.setattr(main_module, "SessionLocal", testing_session_local)
    monkeypatch.setattr(main_module.settings, "seed_on_startup", False)

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_client(db_session):
    client = Client(name="Grupo Nexum S.L.", country="Spain", notes="Test client")
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def seeded_invoice_pair(db_session, sample_client):
    invoice_one = Invoice(
        invoice_number="PAIR-001",
        client_id=sample_client.id,
        issued_on=date(2025, 2, 1),
        due_date=date(2025, 2, 20),
        amount=1200,
        vat_rate=0.21,
        status="collectible",
    )
    invoice_two = Invoice(
        invoice_number="PAIR-002",
        client_id=sample_client.id,
        issued_on=date(2025, 2, 3),
        due_date=date(2025, 2, 22),
        amount=1200,
        vat_rate=0.21,
        status="pending",
    )
    db_session.add_all([invoice_one, invoice_two])
    db_session.commit()
    db_session.refresh(invoice_one)
    db_session.refresh(invoice_two)
    return invoice_one, invoice_two


@pytest.fixture
def clean_match_data(db_session, sample_client):
    invoice = Invoice(
        invoice_number="MATCH-001",
        client_id=sample_client.id,
        issued_on=date(2025, 3, 1),
        due_date=date(2025, 3, 20),
        amount=1550,
        vat_rate=0.21,
        status="collectible",
    )
    transaction = BankTransaction(
        transaction_ref="TX-MATCH-001",
        booked_on=date(2025, 3, 21),
        amount=1550,
        counterparty="Grupo Nexum S.L.",
        reference_text="MATCH-001",
    )
    db_session.add_all([invoice, transaction])
    db_session.commit()
    db_session.refresh(invoice)
    db_session.refresh(transaction)
    return invoice, transaction
