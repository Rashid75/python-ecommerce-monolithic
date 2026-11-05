"""The payments and webhook_events tables.

A payment is a record of money, so the same rules apply as to orders: it is
written once and only moves between states the provider tells us about. The
shop never decides on its own that a payment succeeded.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, get_args

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# pending  - an attempt exists and the provider has told us nothing yet
# succeeded - the provider confirmed the money moved
# failed    - the provider confirmed it did not
# refunded  - the provider confirmed it was sent back
PaymentStatus = Literal["pending", "succeeded", "failed", "refunded"]
PAYMENT_STATUSES: tuple[str, ...] = get_args(PaymentStatus)

_PAYMENT_STATUS_SQL = ", ".join(f"'{status}'" for status in PAYMENT_STATUSES)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    # RESTRICT, as everywhere an order is referenced: the payment is the
    # evidence that money moved for this order, and it must not outlive it
    # as a dangling reference or disappear with it.
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="RESTRICT"), index=True)

    # Which provider this went through, stored rather than assumed. Changing
    # provider later must not make old payments unreadable.
    provider: Mapped[str] = mapped_column(String(30))

    # The provider's own id for this payment. Every webhook names it, and it
    # is the only thing that ties their record to ours.
    reference: Mapped[str] = mapped_column(String(100))

    # Copied from the order at the time the attempt was made, for the same
    # reason order items copy the price: this is what was asked for, and it
    # must stay true even if the order is later changed.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Stored per payment rather than assumed globally. Products still imply
    # a single currency, which remains an open item, but a payment record
    # that does not say what currency it was in is not a record at all.
    currency: Mapped[str] = mapped_column(String(3))

    status: Mapped[PaymentStatus] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(f"status IN ({_PAYMENT_STATUS_SQL})", name="status_is_known"),
        CheckConstraint("amount >= 0", name="amount_not_negative"),
        # One row per provider payment. A webhook that arrives twice cannot
        # create a second payment for the same reference.
        Index("uq_payments_provider_reference", provider, reference, unique=True),
        # The invariant that matters: at most one SUCCEEDED payment per
        # order. Failed attempts may pile up and be retried; a second
        # successful charge for the same order is a double charge, and the
        # database refuses it rather than trusting the code never to.
        Index(
            "uq_payments_one_success_per_order",
            order_id,
            unique=True,
            postgresql_where=text("status = 'succeeded'"),
        ),
    )


class WebhookEvent(Base):
    """Every provider event we have already seen.

    Providers retry. A webhook that is not acknowledged quickly enough, or
    that crosses with a deploy, arrives again - sometimes many times, and
    sometimes out of order. Recording the provider's own event id and
    refusing duplicates is what makes processing one safe to attempt twice.
    """

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    provider: Mapped[str] = mapped_column(String(30))

    # The provider's id for the event, not for the payment. Two different
    # events about the same payment are both legitimate.
    event_id: Mapped[str] = mapped_column(String(100))

    event_type: Mapped[str] = mapped_column(String(50))

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        # The whole deduplication mechanism. The second delivery's INSERT
        # fails here, inside the same transaction that would have applied
        # it, so the effect and the record of it are inseparable.
        Index("uq_webhook_events_provider_event_id", provider, event_id, unique=True),
    )
