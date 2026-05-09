from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str


class InvoiceCreate(BaseModel):
    invoice_number: str
    client_id: int
    issued_on: date
    due_date: date
    amount: float = Field(gt=0)
    vat_rate: float = 0.21
    status: str = "pending"
    notes: str | None = None


class InvoiceRead(InvoiceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ExpenseCreate(BaseModel):
    category: str
    vendor: str
    amount: float = Field(gt=0)
    spent_on: date
    notes: str | None = None


class ExpenseRead(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class BankTransactionCreate(BaseModel):
    transaction_ref: str
    booked_on: date
    amount: float = Field(gt=0)
    counterparty: str
    reference_text: str | None = None


class BankTransactionRead(BankTransactionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reconciled: bool
    needs_review: bool
    review_reason: str | None = None
    matched_invoice_id: int | None = None


class ReconciliationSuggestion(BaseModel):
    transaction_id: int
    transaction_ref: str
    amount: float
    status: str
    review_reason: str | None = None
    candidate_invoice_ids: list[int]
    candidate_invoice_numbers: list[str]


class ReconciliationApplyRequest(BaseModel):
    transaction_id: int
    invoice_id: int


class DashboardResponse(BaseModel):
    revenue_invoiced: float
    expenses_total: float
    collectibles_total: float
    due_soon_invoices: int
    review_queue: int
    vat_estimate: float
    cash_flow: float
    invoice_count: int
    expense_count: int
    transaction_count: int
