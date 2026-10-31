"""The addresses table: a customer's address book.

Working state, not a record. A customer may edit or delete an address at
any time, so an order must never point at a row here - it copies what it
needs instead, exactly as it will copy the price. An order that referenced
addresses.id would have its shipping address silently rewritten when the
customer later corrected a typo, and nobody could answer where the parcel
was actually sent.

Every column here is personal data under PDPL and the UAE and Bahrain
equivalents. Nothing is stored that fulfilment does not need.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# A cap on how many addresses one customer may keep. Not a business rule so
# much as a data-protection one: personal data should not accumulate
# without limit, and nobody legitimately needs hundreds.
MAX_ADDRESSES_PER_USER = 20


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)

    # CASCADE: an address book has no meaning without its owner, and
    # deleting the customer must take their personal data with it. This is
    # safe only because orders copy addresses rather than pointing at them.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # What the customer calls it - "Home", "Office". Theirs to choose, so
    # it is free text rather than a fixed set.
    label: Mapped[str | None] = mapped_column(String(50), default=None)

    # Who receives the parcel, which is not always the account holder.
    recipient_name: Mapped[str] = mapped_column(String(200))

    # Stored as the customer typed it. Normalising to E.164 would be better
    # for dialling, but it needs a library that knows every country's
    # numbering plan, and a wrong "correction" to a delivery number is
    # worse than an unformatted one.
    phone: Mapped[str] = mapped_column(String(30))

    line1: Mapped[str] = mapped_column(String(200))
    line2: Mapped[str | None] = mapped_column(String(200), default=None)
    city: Mapped[str] = mapped_column(String(100))

    # Province, emirate or governorate. Optional because not every address
    # in the region uses one.
    region: Mapped[str | None] = mapped_column(String(100), default=None)

    # Optional on purpose: postal codes are not universally used or
    # required across KSA, the UAE and Bahrain, and demanding one would
    # make valid addresses unenterable.
    postal_code: Mapped[str | None] = mapped_column(String(20), default=None)

    # ISO 3166-1 alpha-2, upper case. Two characters rather than a free
    # text country name, so "UAE", "U.A.E." and "United Arab Emirates"
    # cannot all mean the same place.
    country: Mapped[str] = mapped_column(String(2))

    is_default: Mapped[bool] = mapped_column(server_default="false")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # A partial unique index: unique across the rows where is_default is
        # true, and silent about the rest. One default per customer, decided
        # by the database, so two simultaneous requests cannot both succeed.
        # A plain unique index on (user_id, is_default) would instead allow
        # only one non-default address, which is the opposite of the rule.
        Index(
            "uq_addresses_user_id_default",
            "user_id",
            unique=True,
            postgresql_where=text("is_default"),
        ),
    )
