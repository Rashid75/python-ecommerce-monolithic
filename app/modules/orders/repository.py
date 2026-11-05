"""Database queries for orders. No business rules, and never commits.

Deliberately thin, and deliberately missing an update function for order
lines. There is no way to change one from here because there should be no
way to change one at all - a mistake on an order is corrected by a new
record, not by rewriting the old one.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.orders.models import IdempotencyKey, Order


def add(db: Session, order: Order) -> None:
    """Stage an order and its lines. The caller commits.

    One flush writes both tables: SQLAlchemy inserts the order, reads back
    its generated id, and uses it for the order_items rows. The caller is
    inside a transaction that covers the stock change and the cart clear
    too, so nothing here is durable until that transaction commits.
    """
    db.add(order)
    db.flush()


def get_by_id_for_update(db: Session, order_id: int) -> Order | None:
    """Fetch one order and hold its row until the transaction ends.

    Status changes read the current status and then write a new one, which
    is a read-modify-write and races exactly like stock did in Step 34.
    Without the lock, a payment and a cancellation arriving together could
    both read 'pending' and both believe they were allowed.

    db.get() is not used: it can answer from the session cache without
    going to the database, and a lock has to be taken by the database.
    """
    return db.scalar(select(Order).where(Order.id == order_id).with_for_update())


def list_for_user(db: Session, user_id: int) -> Sequence[Order]:
    """Every order this customer placed, newest first.

    Scoped by user_id in the WHERE clause rather than filtered afterwards,
    so another customer's order cannot be returned even by mistake.

    selectinload fetches all the lines in one extra query instead of one
    per order - the N+1 problem. No pagination yet: a customer with
    thousands of orders would be a problem, and Step 64 is where that gets
    looked at properly rather than guessed at now.
    """
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
    )
    return db.scalars(stmt).all()


def get_for_user(db: Session, user_id: int, order_id: int) -> Order | None:
    """One order, but only if it belongs to this customer.

    The user_id is part of the WHERE clause, not a check afterwards. An
    order belonging to someone else simply does not match, so there is no
    moment where the wrong row is in hand and a forgotten `if` would leak
    it.
    """
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    return db.scalar(stmt)


def claim_idempotency_key(db: Session, user_id: int, key: str, order_id: int) -> None:
    """Record that this key produced this order. The caller commits.

    Flushed immediately so the unique index is consulted now rather than
    at commit. A duplicate raises IntegrityError here, where the caller
    still has a transaction to roll back.
    """
    db.add(IdempotencyKey(user_id=user_id, key=key, order_id=order_id))
    db.flush()


def order_for_key(db: Session, user_id: int, key: str) -> Order | None:
    """The order a previous request with this key produced, if any."""
    stmt = (
        select(Order)
        .join(IdempotencyKey, IdempotencyKey.order_id == Order.id)
        .where(IdempotencyKey.user_id == user_id, IdempotencyKey.key == key)
        .options(selectinload(Order.items))
    )
    return db.scalar(stmt)
