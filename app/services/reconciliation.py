from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BankTransaction, Expense, Invoice
from app.schemas.finance import DashboardResponse, ReconciliationSuggestion


class ReconciliationService:
    def list_suggestions(self, db: Session) -> list[ReconciliationSuggestion]:
        suggestions: list[ReconciliationSuggestion] = []
        open_transactions = db.scalars(
            select(BankTransaction).where(BankTransaction.reconciled.is_(False)).order_by(BankTransaction.booked_on, BankTransaction.id)
        )

        for transaction in open_transactions:
            candidate_rows = db.scalars(
                select(Invoice)
                .where(Invoice.status.in_(["pending", "collectible"]))
                .where(func.abs(Invoice.amount - transaction.amount) <= 0.50)
                .order_by(Invoice.due_date, Invoice.id)
            ).all()

            # Paid invoices stay out of the matching pool. If money is already applied,
            # I don't want the suggestion logic trying to be clever a second time.
            if len(candidate_rows) == 1:
                suggestions.append(
                    ReconciliationSuggestion(
                        transaction_id=transaction.id,
                        transaction_ref=transaction.transaction_ref,
                        amount=transaction.amount,
                        status="clean_match",
                        review_reason=None,
                        candidate_invoice_ids=[candidate_rows[0].id],
                        candidate_invoice_numbers=[candidate_rows[0].invoice_number],
                    )
                )
                transaction.needs_review = False
                transaction.review_reason = None
            elif len(candidate_rows) > 1:
                # If we get more than one match we don't pick one.
                # Better to flag it and let someone check manually.
                suggestions.append(
                    ReconciliationSuggestion(
                        transaction_id=transaction.id,
                        transaction_ref=transaction.transaction_ref,
                        amount=transaction.amount,
                        status="manual_review",
                        review_reason="More than one invoice matches this amount.",
                        candidate_invoice_ids=[invoice.id for invoice in candidate_rows],
                        candidate_invoice_numbers=[invoice.invoice_number for invoice in candidate_rows],
                    )
                )
                transaction.needs_review = True
                transaction.review_reason = "More than one invoice matches this amount."
            else:
                # No amount match means we leave it alone.
                # That usually means bank noise, a partial payment, or a typo.
                suggestions.append(
                    ReconciliationSuggestion(
                        transaction_id=transaction.id,
                        transaction_ref=transaction.transaction_ref,
                        amount=transaction.amount,
                        status="unmatched",
                        review_reason="No open invoice matches this amount.",
                        candidate_invoice_ids=[],
                        candidate_invoice_numbers=[],
                    )
                )
                transaction.needs_review = False
                transaction.review_reason = None

        db.commit()
        return suggestions

    def apply_suggestion(self, db: Session, transaction_id: int, invoice_id: int) -> dict[str, object]:
        transaction = db.get(BankTransaction, transaction_id)
        invoice = db.get(Invoice, invoice_id)
        if transaction is None or invoice is None:
            raise ValueError("Transaction or invoice not found.")
        if transaction.reconciled:
            raise ValueError("Transaction is already reconciled.")
        if invoice.status not in {"pending", "collectible"}:
            raise ValueError("Invoice is not open for reconciliation.")
        if abs(invoice.amount - transaction.amount) > 0.50:
            raise ValueError("Amounts do not match closely enough.")

        # These two updates need to move together.
        # If one fails, I don't want half a reconciliation saved.
        try:
            invoice.status = "paid"
            transaction.reconciled = True
            transaction.needs_review = False
            transaction.review_reason = None
            transaction.matched_invoice_id = invoice.id
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(invoice)
        db.refresh(transaction)
        return {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_status": invoice.status,
            "transaction_id": transaction.id,
            "transaction_ref": transaction.transaction_ref,
            "transaction_reconciled": transaction.reconciled,
        }

    def build_dashboard(self, db: Session) -> DashboardResponse:
        today = date.today()
        due_cutoff = today + timedelta(days=7)

        revenue_invoiced = float(db.scalar(select(func.coalesce(func.sum(Invoice.amount), 0.0))) or 0.0)
        expenses_total = float(db.scalar(select(func.coalesce(func.sum(Expense.amount), 0.0))) or 0.0)
        collectibles_total = float(
            db.scalar(
                select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(Invoice.status.in_(["pending", "collectible", "overdue"]))
            )
            or 0.0
        )
        due_soon_invoices = int(
            db.scalar(
                select(func.count(Invoice.id)).where(Invoice.status.in_(["pending", "collectible"])).where(Invoice.due_date <= due_cutoff)
            )
            or 0
        )
        review_queue = int(db.scalar(select(func.count(BankTransaction.id)).where(BankTransaction.needs_review.is_(True))) or 0)
        paid_total = float(db.scalar(select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(Invoice.status == "paid")) or 0.0)
        vat_estimate = float(db.scalar(select(func.coalesce(func.sum(Invoice.amount * Invoice.vat_rate), 0.0))) or 0.0)

        return DashboardResponse(
            revenue_invoiced=round(revenue_invoiced, 2),
            expenses_total=round(expenses_total, 2),
            collectibles_total=round(collectibles_total, 2),
            due_soon_invoices=due_soon_invoices,
            review_queue=review_queue,
            vat_estimate=round(vat_estimate, 2),
            cash_flow=round(paid_total - expenses_total, 2),
            invoice_count=int(db.scalar(select(func.count(Invoice.id))) or 0),
            expense_count=int(db.scalar(select(func.count(Expense.id))) or 0),
            transaction_count=int(db.scalar(select(func.count(BankTransaction.id))) or 0),
        )


reconciliation_service = ReconciliationService()
