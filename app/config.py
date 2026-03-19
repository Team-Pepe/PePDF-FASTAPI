from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pepdf"

    # JWT
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_days: Optional[int] = None  # None = indefinido (no expira)
    refresh_token_expire_days: int = 30

    # API
    api_title: str = "PePDF API"
    api_version: str = "0.1.0"

    @field_validator("access_token_expire_days", mode="before")
    @classmethod
    def validate_access_token_expire_days(cls, v):
        """Convert empty string to None for indefinite tokens"""
        if v == "" or v == "null":
            return None
        return v

    class Config:
        env_file = ".env"


settings = Settings()
