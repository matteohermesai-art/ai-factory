"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://neon:neon@db:5432/neoncity"
    GRID_WIDTH: int = 100
    GRID_HEIGHT: int = 100
    TICK_INTERVAL_SECONDS: float = 1.0
    LOG_LEVEL: str = "info"
    SEED: int = 42

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
