from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_debug: bool = True
    app_name: str = "KePin API"
    app_version: str = "1.0.0"
    app_api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://kepin:kepin@localhost:5432/kepin"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 10
    database_statement_timeout_ms: int = 10000

    secret_key: str = "kepin-dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    authorization_enabled: bool = False
    sql_echo: bool = False
    log_level: str = "INFO"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "noreply@kepin.io"
    smtp_tls: bool = True
    public_app_url: str = "http://localhost:5173"

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
