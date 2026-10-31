"""What the addresses API accepts and returns."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AddressCreate(BaseModel):
    """A new address."""

    model_config = ConfigDict(extra="forbid")

    label: str | None = Field(default=None, max_length=50)
    recipient_name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=30)
    line1: str = Field(min_length=1, max_length=200)
    line2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    # Two letters, ISO 3166-1 alpha-2. The pattern rejects digits and
    # punctuation; the validator below settles the case.
    country: str = Field(pattern=r"^[A-Za-z]{2}$")
    is_default: bool = False

    @field_validator("country")
    @classmethod
    def upper_case_country(cls, value: str) -> str:
        """Store "bh" and "BH" as the same thing.

        Normalised on the way in rather than compared case-insensitively
        later, because there is exactly one correct spelling and every
        reader would otherwise have to remember to fold the case.
        """
        return value.upper()


class AddressUpdate(BaseModel):
    """A partial update. Only the fields sent are changed."""

    model_config = ConfigDict(extra="forbid")

    label: str | None = Field(default=None, max_length=50)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=30)
    line1: str | None = Field(default=None, min_length=1, max_length=200)
    line2: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}$")
    is_default: bool | None = None

    @field_validator("country")
    @classmethod
    def upper_case_country(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None


class AddressRead(BaseModel):
    """One address. There is no user_id here - it is always yours."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str | None
    recipient_name: str
    phone: str
    line1: str
    line2: str | None
    city: str
    region: str | None
    postal_code: str | None
    country: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
