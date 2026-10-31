"""Database queries for orders. No business rules, and never commits.

Deliberately thin, and deliberately missing an update function for order
lines. There is no way to change one from here because there should be no
way to change one at all - a mistake on an order is corrected by a new
record, not by rewriting the old one.
"""

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
