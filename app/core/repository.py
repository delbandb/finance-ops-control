from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import BankTransaction, Client, Expense, Invoice
from app.schemas.finance import BankTransactionCreate, ExpenseCreate, InvoiceCreate


class FinanceRepository:
    def list_clients(self, db: Session) -> list[Client]:
        return list(db.scalars(select(Client).order_by(Client.name)))

    def list_invoices(self, db: Session) -> list[Invoice]:
        statement = select(Invoice).options(joinedload(Invoice.client)).order_by(Invoice.issued_on.desc(), Invoice.id.desc())
        return list(db.scalars(statement).unique())

    def list_expenses(self, db: Session) -> list[Expense]:
        return list(db.scalars(select(Expense).order_by(Expense.spent_on.desc(), Expense.id.desc())))

    def list_transactions(self, db: Session) -> list[BankTransaction]:
        return list(db.scalars(select(BankTransaction).order_by(BankTransaction.booked_on.desc(), BankTransaction.id.desc())))

    def get_invoice_by_number(self, db: Session, invoice_number: str) -> Invoice | None:
        return db.scalar(select(Invoice).where(Invoice.invoice_number == invoice_number))

    def get_invoice(self, db: Session, invoice_id: int) -> Invoice | None:
        return db.scalar(select(Invoice).where(Invoice.id == invoice_id))

    def get_transaction(self, db: Session, transaction_id: int) -> BankTransaction | None:
        return db.scalar(select(BankTransaction).where(BankTransaction.id == transaction_id))

    def create_invoice(self, db: Session, payload: InvoiceCreate) -> Invoice:
        invoice = Invoice(**payload.model_dump())
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    def create_expense(self, db: Session, payload: ExpenseCreate) -> Expense:
        expense = Expense(**payload.model_dump())
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    def create_transaction(self, db: Session, payload: BankTransactionCreate) -> BankTransaction:
        transaction = BankTransaction(**payload.model_dump())
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction


finance_repository = FinanceRepository()
