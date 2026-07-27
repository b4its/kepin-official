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

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    authorization_enabled: bool = False
    sql_echo: bool = False
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
