# Demo data only. None of this represents real companies or transactions.
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import BankTransaction, Client, Expense, Invoice


def seed_demo_data(db: Session) -> None:
    if db.query(Client).count() > 0:
        return

    clients = [
        Client(name="Grupo Nexum S.L.", country="Spain", notes="Big account. Pays fast when they want to."),
        Client(name="Brindlewick & Co", country="United Kingdom", notes="Same amount invoices on purpose for review cases."),
        Client(name="Solara Tech Europe", country="Spain", notes="Usually pays on time."),
        Client(name="Orbital Foods Iberia", country="Spain", notes="Steady but a bit slow."),
        Client(name="North Harbor Logistics", country="Netherlands", notes="Project-heavy work."),
        Client(name="Velora Studio GmbH", country="Germany", notes="Small but frequent client."),
        Client(name="Asteron Legal Partners", country="Spain", notes="Occasional advisory work."),
        Client(name="Mar de Cobre Trading", country="Portugal", notes="Mixed payment behaviour."),
    ]
    db.add_all(clients)
    db.flush()

    client_map = {client.name: client.id for client in clients}
    base_day = date(2025, 1, 7)

    invoice_rows = [
        ("AF-INV-001", "Grupo Nexum S.L.", 4200, "paid", 0, 20),
        ("AF-INV-002", "Solara Tech Europe", 1800, "paid", 5, 18),
        ("AF-INV-003", "Brindlewick & Co", 1600, "collectible", 8, 14),
        ("AF-INV-004", "Orbital Foods Iberia", 2300, "pending", 11, 21),
        ("AF-INV-005", "North Harbor Logistics", 2750, "paid", 13, 14),
        ("AF-INV-006", "Velora Studio GmbH", 980, "paid", 15, 10),
        ("AF-INV-007", "Asteron Legal Partners", 1250, "overdue", 18, 10),
        ("AF-INV-008", "Mar de Cobre Trading", 2100, "collectible", 20, 15),
        ("AF-INV-009", "Grupo Nexum S.L.", 5100, "paid", 28, 18),
        ("AF-INV-010", "Solara Tech Europe", 1950, "collectible", 31, 16),
        ("AF-INV-011", "Brindlewick & Co", 1600, "collectible", 34, 14),
        ("AF-INV-012", "Orbital Foods Iberia", 2300, "pending", 37, 21),
        ("AF-INV-013", "North Harbor Logistics", 3100, "paid", 41, 20),
        ("AF-INV-014", "Velora Studio GmbH", 1450, "paid", 45, 12),
        ("AF-INV-015", "Asteron Legal Partners", 1700, "overdue", 48, 14),
        ("AF-INV-016", "Mar de Cobre Trading", 2100, "collectible", 52, 15),
        ("AF-INV-017", "Grupo Nexum S.L.", 5400, "paid", 58, 20),
        ("AF-INV-018", "Solara Tech Europe", 2200, "paid", 61, 18),
        ("AF-INV-019", "Brindlewick & Co", 1750, "pending", 65, 16),
        ("AF-INV-020", "Orbital Foods Iberia", 2600, "collectible", 68, 18),
        ("AF-INV-021", "North Harbor Logistics", 3300, "paid", 73, 20),
        ("AF-INV-022", "Velora Studio GmbH", 1100, "pending", 77, 12),
        ("AF-INV-023", "Asteron Legal Partners", 1850, "collectible", 82, 15),
        ("AF-INV-024", "Mar de Cobre Trading", 2950, "overdue", 86, 18),
        ("AF-INV-025", "Grupo Nexum S.L.", 6200, "collectible", 95, 20),
        ("AF-INV-026", "Solara Tech Europe", 2200, "collectible", 99, 16),
        ("AF-INV-027", "Brindlewick & Co", 1750, "pending", 103, 16),
        ("AF-INV-028", "Orbital Foods Iberia", 2800, "paid", 108, 18),
        ("AF-INV-029", "North Harbor Logistics", 3600, "collectible", 112, 20),
        ("AF-INV-030", "Mar de Cobre Trading", 2950, "pending", 118, 18),
    ]

    for invoice_number, client_name, amount, status, offset_days, terms in invoice_rows:
        issued_on = base_day + timedelta(days=offset_days)
        db.add(
            Invoice(
                invoice_number=invoice_number,
                client_id=client_map[client_name],
                issued_on=issued_on,
                due_date=issued_on + timedelta(days=terms),
                amount=amount,
                vat_rate=0.21,
                status=status,
                notes="Seeded demo invoice",
            )
        )

    expense_rows = [
        ("Salaries", "Nomina enero", 4200, 0),
        ("Software", "Notion + Slack", 180, 5),
        ("Marketing", "LinkedIn ads", 420, 12),
        ("Rent", "Office rent January", 950, 15),
        ("Travel", "Client trip Valencia", 240, 19),
        ("Legal", "Outside counsel review", 310, 26),
        ("Salaries", "Nomina febrero", 4250, 31),
        ("Software", "Cloud hosting", 260, 33),
        ("Marketing", "Small campaign test", 390, 40),
        ("Rent", "Office rent February", 950, 45),
        ("Travel", "Train tickets", 130, 51),
        ("Legal", "Contract update", 280, 54),
        ("Salaries", "Nomina marzo", 4300, 61),
        ("Software", "Accounting tools", 310, 64),
        ("Marketing", "Trade fair materials", 560, 70),
        ("Rent", "Office rent March", 950, 75),
        ("Travel", "Barcelona visit", 290, 84),
        ("Legal", "Collections letter", 340, 90),
        ("Salaries", "Nomina abril", 4350, 96),
        ("Software", "CRM seats", 280, 108),
    ]

    for category, vendor, amount, offset_days in expense_rows:
        db.add(
            Expense(
                category=category,
                vendor=vendor,
                amount=amount,
                spent_on=base_day + timedelta(days=offset_days),
                notes="Seeded demo expense",
            )
        )

    transaction_rows = [
        ("TX-001", 4200, "Grupo Nexum S.L.", "AF-INV-001", 21),
        ("TX-002", 1800, "Solara Tech Europe", "AF-INV-002", 25),
        ("TX-003", 1600, "Client payment", "same amount twice", 39),
        ("TX-004", 2300, "Unknown transfer", "same amount twice", 45),
        ("TX-005", 3100, "North Harbor Logistics", "AF-INV-013", 62),
        ("TX-006", 2100, "Bank transfer", "same amount twice", 70),
        ("TX-007", 999, "Noise", "does not match anything", 72),
        ("TX-008", 1750, "Payment received", "same amount twice", 89),
        ("TX-009", 6200, "Grupo Nexum S.L.", "AF-INV-025", 115),
        ("TX-010", 2800, "Orbital Foods Iberia", "AF-INV-028", 126),
        ("TX-011", 2950, "Transfer", "same amount twice", 129),
        ("TX-012", 430, "Stripe payout", "noise", 131),
        ("TX-013", 1450, "Velora Studio GmbH", "AF-INV-014", 58),
        ("TX-014", 2200, "Solara Tech Europe", "AF-INV-026", 123),
        ("TX-015", 5100, "Grupo Nexum S.L.", "AF-INV-009", 48),
    ]

    for transaction_ref, amount, counterparty, reference_text, offset_days in transaction_rows:
        db.add(
            BankTransaction(
                transaction_ref=transaction_ref,
                booked_on=base_day + timedelta(days=offset_days),
                amount=amount,
                counterparty=counterparty,
                reference_text=reference_text,
            )
        )

    db.commit()


def run_seed(db: Session) -> None:
    seed_demo_data(db)


if __name__ == "__main__":
    from app.core.database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        run_seed(session)
        print("Demo data loaded.")
