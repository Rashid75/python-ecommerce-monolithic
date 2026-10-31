"""Database queries for carts. No business rules, and never commits."""

from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.modules.cart.models import Cart, CartItem


def get_by_user_id(db: Session, user_id: int) -> Cart | None:
    """Fetch a user's cart with its lines and their products loaded.

    selectinload issues one extra SELECT per relationship, regardless of how
    many rows come back. Without it, reading item.product in a loop would
    emit one query per line - the N+1 problem - so a ten-line cart would
    cost twelve queries instead of three.

    populate_existing overwrites what the session already holds. Without it,
    a Cart the session created earlier in this request keeps its stale, empty
    items collection and the selectinload result is thrown away - so the
    first add to a new cart returns an empty cart. This function exists to
    produce the current truth for a response, so it must win over the cache.
    """
    stmt = (
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .execution_options(populate_existing=True)
    )
    return db.scalar(stmt)


def get_cart_id(db: Session, user_id: int) -> int | None:
    """Fetch just the id of a user's cart, loading nothing else.

    Used on the paths that are about to change the cart. Loading the lines
    first would put them in the session, and a later read would be answered
    from that copy rather than from the database - which is how a row lock
    gets quietly bypassed.
    """
    return db.scalar(select(Cart.id).where(Cart.user_id == user_id))


def lock_cart(db: Session, cart_id: int) -> None:
    """Hold this cart's row until the transaction ends.

    Every change to a cart goes through here first, so two requests from the
    same customer cannot both read "this product is not in the cart yet" and
    both insert a line. The same lost-update shape as Step 34, prevented the
    same way. Contention is negligible: only one customer ever touches one
    cart.
    """
    db.execute(select(Cart.id).where(Cart.id == cart_id).with_for_update())


def get_item(db: Session, cart_id: int, product_id: int) -> CartItem | None:
    """Fetch one line of a cart, or None."""
    return db.scalar(
        select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    )


def get_items(db: Session, cart_id: int) -> Sequence[CartItem]:
    """Fetch a cart's lines, deliberately without loading their products.

    Checkout needs the product ids and quantities, nothing more. The
    products themselves are read afterwards under a row lock, and loading
    them here first would put unlocked copies in the session that a later
    read could be answered from - the identity-map trap from Step 37.
    """
    return db.scalars(
        select(CartItem).where(CartItem.cart_id == cart_id).order_by(CartItem.id)
    ).all()


def add(db: Session, obj: Cart | CartItem) -> None:
    """Stage a new cart or cart line. The caller commits."""
    db.add(obj)
    db.flush()


def remove_item(db: Session, item: CartItem) -> None:
    """Stage one cart line for deletion. The caller commits."""
    db.delete(item)


def clear_items(db: Session, cart_id: int) -> int:
    """Delete every line of a cart in one statement, returning how many.

    A single DELETE rather than loading the lines and removing them one by
    one: the rows are not needed for anything, so fetching them would be
    work done only to throw it away.
    """
    result = db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
    return result.rowcount
