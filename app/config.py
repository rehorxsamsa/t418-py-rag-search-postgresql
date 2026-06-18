from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration loaded from environment variables."""

    database_url: str = "postgresql://appuser:secret@db:5432/semantic"
    anthropic_api_key: str = ""
    embedding_provider: str = "local"  # "local" (sentence-transformers) or "voyage"
    embedding_dim: int = 384  # all-MiniLM-L6-v2 output dimension

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
