from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DB_PATH = Path(tempfile.gettempdir()) / "finance-ops-control" / "finance_ops_control.db"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "Finance Ops Control")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
    seed_on_startup: bool = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-before-real-deploy")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")


settings = Settings()
