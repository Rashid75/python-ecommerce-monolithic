"""Application settings, read from environment variables and the .env file."""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, model_validator
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

    # --- Logging ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # --- Authentication ---
    # No default, for the same reason as the database password: a default
    # secret is one an attacker already knows, and defaults get deployed.
    # Anyone holding this value can mint a token for any account.
    jwt_secret: SecretStr
    # HS256 signs with this one shared secret. Fine for a single service.
    jwt_algorithm: str = "HS256"
    # Short-lived on purpose. A stolen token stays usable until it expires,
    # and nothing here can revoke one early.
    jwt_expire_minutes: int = Field(default=30, ge=1, le=1440)

    # --- Web ---
    # Browsers that may call this API from a page. Empty by default: a
    # misconfigured CORS policy is how a cookie-authenticated API gets read
    # by someone else's site, and "allow nothing" is the only safe default
    # to ship. Set it explicitly per environment.
    cors_origins: tuple[str, ...] = ()

    # --- Payments ---
    # Only one option today. A Literal rather than a plain string so a typo
    # in the environment fails at startup instead of at the first payment.
    payment_provider: Literal["sandbox"] = "sandbox"

    # ISO 4217, three letters. Stored on every payment rather than assumed,
    # though products still imply a single currency.
    payment_currency: str = Field(default="BHD", pattern=r"^[A-Z]{3}$")

    # No default, for the same reason as jwt_secret. Anyone holding this
    # can forge a webhook saying an order was paid, so it is exactly as
    # sensitive as the token secret.
    payment_webhook_secret: SecretStr

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
    def check_secrets_are_real(self) -> "Settings":
        """Refuse to start on a placeholder or an obviously weak secret.

        The .env.example in this repository ships CHANGE_ME values on
        purpose, and the failure mode this guards against is somebody
        copying it, getting a working application, and never going back.

        The length floor applies in production only. Local development is
        allowed a short secret; a deployment is not, because 32 bytes is
        the point below which guessing a HS256 signing key stops being
        theoretical.
        """
        secrets = {
            "APP_DB_PASSWORD": self.db_password,
            "APP_JWT_SECRET": self.jwt_secret,
            "APP_PAYMENT_WEBHOOK_SECRET": self.payment_webhook_secret,
        }
        for name, secret in secrets.items():
            value = secret.get_secret_value()
            if not value or "CHANGE_ME" in value:
                raise ValueError(f"{name} is still the example value")
            if self.is_production and len(value) < 32:
                raise ValueError(f"{name} must be at least 32 characters in production")
        return self

    @model_validator(mode="after")
    def check_production_is_safe(self) -> "Settings":
        # Both of these print internal details that clients must never see.
        if self.is_production and (self.debug or self.db_echo):
            raise ValueError("APP_DEBUG and APP_DB_ECHO must be false in production")
        # The sandbox provider moves no money. Running it in production
        # would mean orders being marked paid for nothing, so the
        # application refuses to start rather than discovering this at the
        # first checkout.
        if self.is_production and self.payment_provider == "sandbox":
            raise ValueError("APP_PAYMENT_PROVIDER must not be 'sandbox' in production")
        # "*" would let any site on the internet make authenticated calls
        # from a victim's browser. There is no production case for it.
        if self.is_production and "*" in self.cors_origins:
            raise ValueError("APP_CORS_ORIGINS must not include '*' in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Read the settings once, then reuse the same object."""
    return Settings()
