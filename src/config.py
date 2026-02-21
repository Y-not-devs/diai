from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Diagnosis AI Assistant API"
    APP_VERSION: str = "0.1.0"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False

    # Model
    MODEL_ID: str
    HF_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()