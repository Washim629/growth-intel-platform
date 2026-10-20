"""
Centralized application configuration.

Everything secret or environment-specific is read from environment
variables (loaded from a local .env file in development). Nothing here
is hardcoded into source control - copy .env.example to .env and fill
in real values.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./growth_intel.db"

    # Auth
    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Email login codes
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "growthanalyzer@gmail.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "growthanalyzer@gmail.com"
    SMTP_USE_TLS: bool = True
    LOGIN_OTP_EXPIRE_MINUTES: int = 10
    LOGIN_OTP_RESEND_SECONDS: int = 60

    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # App
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"
    MAX_UPLOAD_MB: int = 25

    @property
    def cors_origins_list(self) -> List[str]:
        raw = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return raw or ["*"]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()
