from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(min_length=1)
    app_env: str = Field(default="local", pattern="^(local|staging|production)$")
    log_level: str = Field(default="INFO")
    data_file_path: str = Field(min_length=1)
    llm_api_key: str = Field(default="")
