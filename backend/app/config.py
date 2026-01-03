from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Database - individual components (handles special characters in password)
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "newsagg"
    db_password: str = "newsagg_secret"
    db_name: str = "geopolitical_news"

    # Legacy support - will be overridden by individual components if set
    database_url: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        """Build database URL from components, properly escaping password"""
        if self.database_url and "db_host" not in str(self.database_url):
            return self.database_url
        # URL-encode the password to handle special characters
        encoded_password = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI/LLM Configuration
    groq_api_key: str = ""
    llm_provider: str = "groq"  # groq or ollama
    llm_model: str = "llama-3.1-8b-instant"  # Smaller model for scoring (less tokens)
    llm_model_large: str = "llama-3.3-70b-versatile"  # Larger model for summaries
    ollama_base_url: str = "http://localhost:11434"  # For future Ollama support

    # Application
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # News Fetching
    fetch_interval_minutes: int = 30
    max_articles_per_source: int = 50

    # External API Keys (optional)
    twitter_bearer_token: str = ""  # Twitter/X API
    newsapi_key: str = ""  # NewsAPI.org
    mediastack_key: str = ""  # Mediastack API

    # Relevance Scoring Weights
    geo_weight: float = 0.35
    military_weight: float = 0.30
    diplomatic_weight: float = 0.20
    economic_weight: float = 0.15

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
