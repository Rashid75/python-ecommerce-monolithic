"""Database queries for addresses.

Every query takes user_id and filters on it. A customer cannot name
another customer's address, because the id alone never identifies a row.
"""

from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.addresses.models import Address


def list_for_user(db: Session, user_id: int) -> Sequence[Address]:
    """Every address this customer has, default first, then oldest first."""
    stmt = (
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.id)
    )
    return db.scalars(stmt).all()


def get_for_user(db: Session, user_id: int, address_id: int) -> Address | None:
    """One address, but only if it belongs to this customer.

    user_id is part of the WHERE clause rather than checked afterwards.
    A forgotten check is a data leak; a missing WHERE clause is a query
    that returns nothing.
    """
    return db.scalar(select(Address).where(Address.id == address_id, Address.user_id == user_id))


def count_for_user(db: Session, user_id: int) -> int:
    stmt = select(Address.id).where(Address.user_id == user_id)
    return len(db.scalars(stmt).all())


def clear_default(db: Session, user_id: int, except_id: int | None = None) -> None:
    """Unset whichever address is currently the default.

    Runs before the new default is set, in the same transaction, so the
    partial unique index never sees two. except_id avoids pointlessly
    rewriting the row that is about to be set anyway.
    """
    stmt = update(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
    if except_id is not None:
        stmt = stmt.where(Address.id != except_id)
    db.execute(stmt.values(is_default=False))


def add(db: Session, address: Address) -> None:
    db.add(address)
    db.flush()


def remove(db: Session, address: Address) -> None:
    db.delete(address)
