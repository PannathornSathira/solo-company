import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://solo_company:solo_company@localhost:5432/solo_company",
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
