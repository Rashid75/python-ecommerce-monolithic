"""Database queries for products.

Only queries live here. No business rules, no HTTP concepts. Each function
takes the session as its first argument, so the caller controls the
transaction - these functions never commit.
"""

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session

from app.modules.products.models import Product

# Only these columns may be sorted on. The query parameter is looked up in
# this dict, never put into the SQL itself: a column name cannot be a bound
# parameter, so interpolating one straight from a request would be an
# injection hole. An unknown key simply fails the lookup.
SORTABLE_COLUMNS = {
    "id": Product.id,
    "name": Product.name,
    "price": Product.price,
    "created_at": Product.created_at,
}


def get_by_id(db: Session, product_id: int) -> Product | None:
    """Fetch one product by primary key, or None."""
    # db.get() is the shortcut for a primary-key lookup. It also checks the
    # session first, so an object already loaded is not fetched again.
    return db.get(Product, product_id)


def get_by_sku(db: Session, sku: str) -> Product | None:
    """Fetch one product by its SKU, or None."""
    # scalar() returns the first column of the first row, or None.
    return db.scalar(select(Product).where(Product.sku == sku))


def _filters(
    search: str | None,
    is_active: bool | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
) -> list[ColumnElement[bool]]:
    """Build the WHERE conditions shared by the list and count queries.

    Returning conditions rather than a finished query means the two cannot
    drift apart and report different totals.
    """
    conditions: list[ColumnElement[bool]] = []
    if search:
        # ilike is case-insensitive LIKE. The pattern is a bound parameter,
        # so the value never becomes part of the SQL text.
        pattern = f"%{search}%"
        conditions.append(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
    if is_active is not None:
        conditions.append(Product.is_active == is_active)
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)
    return conditions


def list_products(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    is_active: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: str = "id",
    descending: bool = False,
) -> Sequence[Product]:
    """Fetch one page of products."""
    column = SORTABLE_COLUMNS[sort]
    stmt = (
        select(Product)
        .where(*_filters(search, is_active, min_price, max_price))
        .order_by(column.desc() if descending else column.asc())
        # id is unique, so adding it makes the order total. Without a
        # tiebreaker, rows with equal prices can swap between pages and a
        # product appears twice or not at all.
        .order_by(Product.id)
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


def count_products(
    db: Session,
    *,
    search: str | None = None,
    is_active: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> int:
    """Count products matching the same filters, ignoring limit and offset."""
    stmt = (
        select(func.count())
        .select_from(Product)
        .where(*_filters(search, is_active, min_price, max_price))
    )
    return db.scalar(stmt) or 0


def add(db: Session, product: Product) -> Product:
    """Stage a new product and get its generated id."""
    db.add(product)
    # flush() sends the INSERT so PostgreSQL assigns the id, but does not
    # commit. The caller decides whether the whole unit of work succeeds.
    db.flush()
    return product


def remove(db: Session, product: Product) -> None:
    """Stage a product for deletion. The caller commits."""
    db.delete(product)


# There is no update() function on purpose. SQLAlchemy tracks changes to an
# object loaded in a session, so the service simply assigns new values and
# the UPDATE is emitted on the next flush or commit.
