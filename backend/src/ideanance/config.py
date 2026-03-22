"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchored paths — CWD-independent
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(PROJECT_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM Providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    domain_model: str = "anthropic:claude-sonnet-4-6"
    routing_model: str = "anthropic:claude-haiku-4-5"
    embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = (
        f"sqlite+aiosqlite:///{BACKEND_DIR / 'ideanance.db'}"
    )

    # Application
    app_env: str = "development"
    debug: bool = False
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"]
    )
    secret_key: str = "change-me-in-production"

    # Observability
    logfire_token: str = ""
    logfire_service_name: str = "ideanance"

    # Feature flags
    enable_streaming: bool = True
    enable_auth: bool = False

    # Kill switches
    agents_enabled: bool = True

    # Rate limiting
    rate_limit_max_requests: int = 30
    rate_limit_window_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


settings = Settings()
