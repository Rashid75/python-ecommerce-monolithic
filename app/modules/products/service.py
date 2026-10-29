"""Business rules for products.

The service decides what is allowed and when a change is finished, and it
owns the transaction: it is the only layer that calls commit().

It raises application errors, never HTTP errors. Turning those into status
codes is the router's job.
"""

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, InsufficientStockError, NotFoundError
from app.modules.categories import repository as category_repo
from app.modules.products import repository as repo
from app.modules.products.models import Product
from app.modules.products.schemas import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Product:
    """Return one product, or raise if it does not exist."""
    product = repo.get_by_id(db, product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} does not exist")
    return product


def list_products(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    is_active: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    category_id: int | None = None,
    in_stock: bool | None = None,
    sort: str = "id",
    descending: bool = False,
) -> tuple[Sequence[Product], int]:
    """Return one page of products and the total number that match.

    Both queries use the same filters, so the total always describes the
    same set the page was taken from.
    """
    filters = {
        "search": search,
        "is_active": is_active,
        "min_price": min_price,
        "max_price": max_price,
        "category_id": category_id,
        "in_stock": in_stock,
    }
    items = repo.list_products(
        db, limit=limit, offset=offset, sort=sort, descending=descending, **filters
    )
    total = repo.count_products(db, **filters)
    return items, total


def _check_category_exists(db: Session, category_id: int | None) -> None:
    """Reject a category id that does not exist.

    The foreign key would also stop it, but the database error says nothing
    useful to a client. Checking here produces a clear 404 instead.
    """
    if category_id is None:
        return
    if category_repo.get_by_id(db, category_id) is None:
        raise NotFoundError(f"Category {category_id} does not exist")


def create_product(db: Session, data: ProductCreate) -> Product:
    """Create a product, rejecting a SKU that is already taken."""
    _check_category_exists(db, data.category_id)
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
    changes = data.model_dump(exclude_unset=True)
    if "category_id" in changes:
        _check_category_exists(db, changes["category_id"])
    # exclude_unset keeps fields the client did not send untouched.
    # Without it every absent field would arrive as None and wipe good data.
    for field, value in changes.items():
        setattr(product, field, value)
    db.commit()
    return product


def adjust_stock(db: Session, product_id: int, change: int) -> Product:
    """Add to or take from a product's stock and return its new state.

    change is a difference, not a new total: +10 for a delivery, -1 for a
    sale. The caller never has to know the current quantity, so it cannot
    send a stale one.

    Known gap, fixed in Step 34: this reads the quantity, adds to it in
    Python, and writes the result back. Two requests arriving together can
    both read 5 and both write 4, so one sale is lost. The check constraint
    still stops the total going negative, so the data cannot become
    nonsense - but it can become wrong. Step 34 moves the arithmetic into
    the database, where the read and the write are a single operation.
    """
    product = get_product(db, product_id)
    new_quantity = product.stock_quantity + change
    if new_quantity < 0:
        # Refuse the whole adjustment rather than clamping to zero. Clamping
        # would report success for a sale that could not be fulfilled.
        raise InsufficientStockError(
            f"Product {product_id} has {product.stock_quantity} in stock, "
            f"so {abs(change)} cannot be removed"
        )
    product.stock_quantity = new_quantity
    db.commit()
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    repo.remove(db, product)
    db.commit()
