"""Business rules for the cart. The only layer that commits.

Every function takes the user id rather than a cart id. A caller cannot
name a cart, so it cannot name someone else's.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.cart import repository as repo
from app.modules.cart.models import Cart, CartItem
from app.modules.cart.schemas import MAX_QUANTITY
from app.modules.products import repository as product_repo


def _ensure_cart_id(db: Session, user_id: int) -> int:
    """Return this user's cart id, creating the cart the first time.

    A cart is implicit: every signed-in customer conceptually has one. It is
    created on first use rather than at registration, so customers who never
    shop leave no row behind.

    Only the id is loaded. The lines are left alone on purpose - see
    repository.get_cart_id.
    """
    cart_id = repo.get_cart_id(db, user_id)
    if cart_id is not None:
        return cart_id
    cart = Cart(user_id=user_id)
    try:
        repo.add(db, cart)
        db.commit()
    except IntegrityError:
        # Two requests from the same customer arrived together and both
        # found no cart. uq_carts_user_id let exactly one of them win; this
        # is the other one, so read the winner's cart instead of failing.
        db.rollback()
        cart_id = repo.get_cart_id(db, user_id)
        if cart_id is None:
            raise
        return cart_id
    return cart.id


def get_cart(db: Session, user_id: int) -> Cart:
    """The whole cart, with its lines and their products, ready for a response.

    An empty cart is the correct answer to "show me my cart", not a 404.
    """
    _ensure_cart_id(db, user_id)
    cart = repo.get_by_user_id(db, user_id)
    if cart is None:
        # The cart was created or found a moment ago, so this cannot happen
        # unless something deleted it in between.
        raise NotFoundError("Cart could not be loaded")
    return cart


def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
    """Add a product to the cart, or add more of one already there.

    Availability is deliberately not checked here. Whether the product is
    active, and whether there is enough stock, are Steps 39 and 40 - those
    are decisions about what to tell the customer, not arithmetic.
    """
    if product_repo.get_by_id(db, product_id) is None:
        raise NotFoundError(f"Product {product_id} does not exist")

    cart_id = _ensure_cart_id(db, user_id)
    # Lock first, read afterwards. Two simultaneous adds of the same product
    # would otherwise both see no line and both insert one, and the unique
    # index would turn the loser into a 500. Reading the line before taking
    # the lock is just as broken: the session would answer the later read
    # from the copy it already held, so the lock would protect nothing.
    repo.lock_cart(db, cart_id)

    item = repo.get_item(db, cart_id, product_id)
    new_quantity = quantity if item is None else item.quantity + quantity
    if new_quantity > MAX_QUANTITY:
        db.rollback()
        raise ValidationError(f"A cart line cannot hold more than {MAX_QUANTITY} of one product")

    if item is None:
        repo.add(db, CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity))
    else:
        item.quantity = new_quantity
    db.commit()

    # Re-read so the response carries the products, which the lock query and
    # the insert above did not load.
    return get_cart(db, user_id)
