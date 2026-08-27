import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # System Identification
    APP_NAME: str = "Fídíò Studio API"
    APP_ENV: str = Field(default="development", description="development, staging, production")
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # PostgreSQL Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fidio-studio"
    POSTGRES_USER: str = "fidio-studio"
    POSTGRES_PASSWORD: str = "OmolileOtilile"
    POSTGRES_SSLMODE: str = "prefer"

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # MinIO / S3 Configuration
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_EXTERNAL_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "fidio-minio-admin"
    MINIO_SECRET_KEY: str = "fidio-minio-secret-key-2026"
    MINIO_BUCKET_MEDIA: str = "fidio-media"
    MINIO_BUCKET_RENDERS: str = "fidio-renders"
    MINIO_USE_SSL: bool = False

    # AI Provider Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_PLANNING: str = "anthropic/claude-3.5-sonnet"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL SQLAlchemy Connection String (Asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        """Construct PostgreSQL Sync Connection String (Psycopg2 for Alembic/Celery)."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis Connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
