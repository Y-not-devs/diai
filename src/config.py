# src/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Diagnosis AI Assistant API"
    APP_VERSION: str = "0.1.0"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False

    # Model
    MODEL_ID: str
    HF_TOKEN: str

    # ChatBot mode
    # 0 = offline only
    # 1 = offline + auto-update
    # 2 = offline + auto-update + token
    CHAT_BOT_MODE: int = 0

    # Paths
    DATA_PATH: str = "./data"
    MODEL_PATH: str = "./qwen"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()