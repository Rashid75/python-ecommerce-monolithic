"""Database queries for products.

Only queries live here. No business rules, no HTTP concepts. Each function
takes the session as its first argument, so the caller controls the
transaction - these functions never commit.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.models import Product


def get_by_id(db: Session, product_id: int) -> Product | None:
    """Fetch one product by primary key, or None."""
    # db.get() is the shortcut for a primary-key lookup. It also checks the
    # session first, so an object already loaded is not fetched again.
    return db.get(Product, product_id)


def get_by_sku(db: Session, sku: str) -> Product | None:
    """Fetch one product by its SKU, or None."""
    # scalar() returns the first column of the first row, or None.
    return db.scalar(select(Product).where(Product.sku == sku))


def list_products(db: Session, limit: int = 20, offset: int = 0) -> Sequence[Product]:
    """Fetch a page of products, newest last.

    limit and offset are always applied. A query with no limit works fine on
    ten rows and takes the server down on ten million.
    """
    stmt = select(Product).order_by(Product.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()


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
