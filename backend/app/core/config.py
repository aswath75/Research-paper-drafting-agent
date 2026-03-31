from pathlib import Path
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_ENV_FILE = BASE_DIR.parent / ".env"
BACKEND_ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Research Paper Drafting System"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "research_drafter"
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    semantic_scholar_api_key: str | None = None
    crossref_base_url: str = "https://api.crossref.org/works"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_ENV_FILE), str(ROOT_ENV_FILE)),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
