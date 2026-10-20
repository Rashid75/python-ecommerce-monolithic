"""Application settings, read from environment variables and the .env file."""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Each field reads an APP_ prefixed variable: name <- APP_NAME."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        # .env is shared with docker-compose.yml, so ignore anything we
        # do not declare here instead of raising an error.
        extra="ignore",
        frozen=True,
    )

    # --- Application ---
    name: str = "Python Ecommerce API"
    environment: Literal["local", "staging", "production"] = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_user: str
    db_name: str
    # No default. A default password would eventually get deployed.
    # SecretStr hides the value from logs and error messages.
    db_password: SecretStr
    # Print every SQL statement. Handy while learning.
    db_echo: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def database_url(self) -> str:
        """The connection string SQLAlchemy needs."""
        # quote_plus escapes characters like @ or / that would break the URL.
        password = quote_plus(self.db_password.get_secret_value())
        return (
            f"postgresql+psycopg://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @model_validator(mode="after")
    def check_production_is_safe(self) -> "Settings":
        # Both of these print internal details that clients must never see.
        if self.is_production and (self.debug or self.db_echo):
            raise ValueError("APP_DEBUG and APP_DB_ECHO must be false in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Read the settings once, then reuse the same object."""
    return Settings()
