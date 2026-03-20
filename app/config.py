from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List


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

    # CORS - Load all values from .env
    frontend_url: str  # FRONTEND_URL from .env (required)
    cors_allow_credentials: bool = True  # CORS_ALLOW_CREDENTIALS from .env
    cors_allow_origins_str: str = ""  # CORS_ALLOW_ORIGINS from .env (comma-separated)

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string in .env"""
        if not self.cors_allow_origins_str:
            return []
        return [origin.strip() for origin in self.cors_allow_origins_str.split(",") if origin.strip()]

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
