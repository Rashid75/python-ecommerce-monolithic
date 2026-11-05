"""Database queries for payments. No business rules, and never commits."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payments.models import Payment, WebhookEvent


def add(db: Session, obj: Payment | WebhookEvent) -> None:
    """Stage a payment or an event. The caller commits.

    Flushed immediately so a unique index is consulted now, while the
    caller still has a transaction to roll back, rather than at commit.
    """
    db.add(obj)
    db.flush()


def get_by_reference_for_update(db: Session, provider: str, reference: str) -> Payment | None:
    """Fetch a payment by the provider's reference and lock its row.

    Locked because applying an event is a read-modify-write on the status,
    and providers happily deliver two events at once. Without the lock a
    succeeded and a failed event arriving together could both read
    'pending'.
    """
    stmt = (
        select(Payment)
        .where(Payment.provider == provider, Payment.reference == reference)
        .with_for_update()
    )
    return db.scalar(stmt)


def list_for_order(db: Session, order_id: int) -> list[Payment]:
    """Every payment attempt against one order, oldest first."""
    stmt = select(Payment).where(Payment.order_id == order_id).order_by(Payment.id)
    return list(db.scalars(stmt).all())


def succeeded_for_order(db: Session, order_id: int) -> Payment | None:
    """The one successful payment for an order, if there is one.

    At most one can exist: a partial unique index enforces it.
    """
    stmt = select(Payment).where(Payment.order_id == order_id, Payment.status == "succeeded")
    return db.scalar(stmt)
