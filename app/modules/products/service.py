"""Business rules for products.

The service decides what is allowed and when a change is finished, and it
owns the transaction: it is the only layer that calls commit().

It raises application errors, never HTTP errors. Turning those into status
codes is the router's job.
"""

from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.modules.products import repository as repo
from app.modules.products.models import Product
from app.modules.products.schemas import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Product:
    """Return one product, or raise if it does not exist."""
    product = repo.get_by_id(db, product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} does not exist")
    return product


def list_products(db: Session, limit: int = 20, offset: int = 0) -> Sequence[Product]:
    return repo.list_products(db, limit=limit, offset=offset)


def create_product(db: Session, data: ProductCreate) -> Product:
    """Create a product, rejecting a SKU that is already taken."""
    product = Product(**data.model_dump())
    try:
        repo.add(db, product)
        db.commit()
    except IntegrityError as exc:
        # Let the database decide. Checking for the SKU first would leave a
        # gap between the check and the insert, and two requests arriving
        # together could both pass it. The unique constraint cannot be raced.
        # products has only one unique constraint, so this is the SKU.
        db.rollback()
        raise AlreadyExistsError(f"SKU {data.sku} is already in use") from exc
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    """Apply a partial update to an existing product."""
    product = get_product(db, product_id)
    # exclude_unset keeps fields the client did not send untouched.
    # Without it every absent field would arrive as None and wipe good data.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    repo.remove(db, product)
    db.commit()
