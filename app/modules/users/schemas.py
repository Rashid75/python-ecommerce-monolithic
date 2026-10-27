"""What the users API accepts and returns."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Registration request."""

    # EmailStr rejects anything that is not a valid address, before any
    # code runs. It needs the email-validator package.
    email: EmailStr

    # min_length is a floor, not a policy. max_length matters too: Argon2
    # takes longer on longer input, so without a cap a huge password body
    # becomes a cheap way to burn server CPU.
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    """What the API sends back about a user.

    password_hash is absent, and that absence is the protection. Fields not
    listed here are never serialised, so the hash cannot leak by accident
    even though it sits right next to these columns on the model.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    created_at: datetime
