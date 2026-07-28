import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://solo_company:solo_company@localhost:5432/solo_company",
        )
        self.runtime_model_backend: str = os.getenv(
            "RUNTIME_MODEL_BACKEND", "fake"
        )
        self.graph_version: str = os.getenv("GRAPH_VERSION", "p1-v1")
        self.gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
        self.gemini_model_id: str = os.getenv(
            "GEMINI_MODEL_ID", "gemini-3.1-pro-preview"
        )
        configured_langgraph_url = os.getenv("LANGGRAPH_DATABASE_URL")
        self.langgraph_database_url: str = (
            configured_langgraph_url
            if configured_langgraph_url
            else self.database_url.replace(
                "postgresql+psycopg://", "postgresql://"
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
