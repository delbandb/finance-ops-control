from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if settings.seed_on_startup:
            seed_demo_data(session)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend for invoices, expenses, bank transactions, and reconciliation work.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)
