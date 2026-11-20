from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from airaware.db.url import to_asyncpg_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "airaware"
    app_env: str = "local"
    log_level: str = "INFO"
    data_file: Path = Path("data/sample_records.json")
    database_url: str = "postgresql+asyncpg://localhost:5432/airaware"
    # The commit this image was built from. CI sets it (Dockerfile ARG GIT_SHA).
    git_sha: str = "dev"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        return to_asyncpg_url(v)


@lru_cache
def get_settings() -> Settings:
    return Settings()
