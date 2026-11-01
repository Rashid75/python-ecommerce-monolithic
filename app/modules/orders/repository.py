"""Database queries for orders. No business rules, and never commits.

Deliberately thin, and deliberately missing an update function for order
lines. There is no way to change one from here because there should be no
way to change one at all - a mistake on an order is corrected by a new
record, not by rewriting the old one.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.orders.models import Order


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
