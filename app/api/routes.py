from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.repository import finance_repository
from app.schemas.finance import (
    BankTransactionCreate,
    BankTransactionRead,
    DashboardResponse,
    ExpenseCreate,
    ExpenseRead,
    InvoiceCreate,
    InvoiceRead,
    ReconciliationApplyRequest,
    ReconciliationSuggestion,
)
from app.services.reconciliation import reconciliation_service


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    metrics = reconciliation_service.build_dashboard(db)
    suggestions = reconciliation_service.list_suggestions(db)[:5]
    invoices = finance_repository.list_invoices(db)[:5]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"metrics": metrics, "suggestions": suggestions, "invoices": invoices},
    )


@router.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/invoices", response_model=list[InvoiceRead])
def list_invoices(db: Session = Depends(get_db)):
    return finance_repository.list_invoices(db)


@router.post("/api/invoices", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    if finance_repository.get_invoice_by_number(db, payload.invoice_number):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice number already exists.")
    return finance_repository.create_invoice(db, payload)


@router.get("/api/expenses", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)):
    return finance_repository.list_expenses(db)


@router.post("/api/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    return finance_repository.create_expense(db, payload)


@router.get("/api/transactions", response_model=list[BankTransactionRead])
def list_transactions(db: Session = Depends(get_db)):
    return finance_repository.list_transactions(db)


@router.post("/api/transactions", response_model=BankTransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: BankTransactionCreate, db: Session = Depends(get_db)):
    return finance_repository.create_transaction(db, payload)


@router.get("/api/reconciliation/suggestions", response_model=list[ReconciliationSuggestion])
def get_reconciliation_suggestions(db: Session = Depends(get_db)):
    return reconciliation_service.list_suggestions(db)


@router.post("/api/reconciliation/apply")
def apply_reconciliation(payload: ReconciliationApplyRequest, db: Session = Depends(get_db)):
    try:
        return reconciliation_service.apply_suggestion(db, payload.transaction_id, payload.invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return reconciliation_service.build_dashboard(db)
