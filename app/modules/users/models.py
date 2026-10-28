"""The users table."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"
ROLES = (ROLE_CUSTOMER, ROLE_ADMIN)


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

    # "customer" or "admin". Everyone who registers is a customer; nothing
    # in the API can set this, so it is changed by an administrator in the
    # database. See ROLE_CUSTOMER / ROLE_ADMIN below.
    #
    # A plain String with a check constraint rather than a PostgreSQL ENUM
    # type: adding a third role later is then an ordinary constraint change
    # instead of ALTER TYPE, which is awkward inside a transaction.
    role: Mapped[str] = mapped_column(String(20), server_default="customer")

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
        # The database rejects an unknown role, so a typo in a manual UPDATE
        # cannot leave an account in a state the code does not understand.
        CheckConstraint("role in ('customer', 'admin')", name="role_is_known"),
    )
