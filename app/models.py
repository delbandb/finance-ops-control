from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    issued_on: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[float] = mapped_column(Float)
    vat_rate: Mapped[float] = mapped_column(Float, default=0.21)
    status: Mapped[str] = mapped_column(String(20), index=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="invoices")
    matched_transactions: Mapped[list["BankTransaction"]] = relationship(back_populates="matched_invoice")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    vendor: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float)
    spent_on: Mapped[date] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_ref: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    booked_on: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[float] = mapped_column(Float, index=True)
    counterparty: Mapped[str] = mapped_column(String(120))
    reference_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    reconciled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    review_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    matched_invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), nullable=True)

    matched_invoice: Mapped["Invoice | None"] = relationship(back_populates="matched_transactions")
