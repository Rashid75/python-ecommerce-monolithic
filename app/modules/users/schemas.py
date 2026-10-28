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


class LoginRequest(BaseModel):
    """Sign-in request.

    No length rules on the password here. The stored one was checked at
    registration, and rejecting a short attempt with 422 instead of 401
    would quietly leak that the real password is longer than that.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """What a successful sign-in returns."""

    access_token: str
    # "bearer" tells the client to send it as: Authorization: Bearer <token>
    token_type: str = "bearer"


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
