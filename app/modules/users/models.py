"""The users table."""

from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(320))

    # The Argon2 hash, never the password. Nothing in this project ever
    # stores or logs a plaintext password, and no API response includes
    # this column - UserRead in Step 25 simply will not list it.
    #
    # 255 is generous: an Argon2 hash is around 100 characters, but the
    # string also carries the algorithm and parameters, which change when
    # the cost settings are raised.
    password_hash: Mapped[str] = mapped_column(String(255))

    # Lets an account be disabled without deleting it, so its past orders
    # still make sense. Same reasoning as is_active on products.
    is_active: Mapped[bool] = mapped_column(server_default="true")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # Case-insensitive, like SKU and category name in Step 23.
        # Nobody expects Rashid@x.com and rashid@x.com to be two accounts,
        # and allowing both invites confusion at sign-in and impersonation
        # through a lookalike address.
        Index("uq_users_lower_email", func.lower(email), unique=True),
    )
