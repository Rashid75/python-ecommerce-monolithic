"""Business rules for orders. The only layer that commits.

This module owns the one thing that makes an order a record rather than a
view: the moment the product's details stop being looked up and start being
copied. Checkout is the transaction around that moment.
"""

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmptyCartError,
    NotFoundError,
    PriceChangedError,
    UnavailableError,
)
from app.modules.addresses import service as address_service
from app.modules.addresses.schemas import ShippingAddress
from app.modules.cart import repository as cart_repo
from app.modules.orders import repository as repo
from app.modules.orders.models import Order, OrderItem
from app.modules.products import repository as product_repo
from app.modules.products.models import Product


def build_order(
    user_id: int,
    shipping: ShippingAddress,
    lines: Sequence[tuple[Product, int]],
) -> Order:
    """Turn locked products and quantities into an unsaved Order.

    The products must already be locked and checked by the caller - that is
    Step 47's job, and the values read here are only correct because of it.
    Nothing is written: the caller adds the result inside its own
    transaction.

    Every field on a line is a copy taken now. After this returns, the order
    never reads products again, so renaming, repricing or retiring the
    product tomorrow cannot change what the customer bought or what they
    paid.
    """
    items = [
        OrderItem(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            unit_price=product.price,
            quantity=quantity,
        )
        for product, quantity in lines
    ]

    # Summed from the copies above, not from product.price a second time.
    # Reading the live price again would let the total disagree with the
    # lines it is supposed to be the sum of. Decimal throughout: these are
    # exact values, and sum() needs a Decimal to start from so it never
    # mixes an int 0 into the arithmetic.
    total = sum((item.unit_price * item.quantity for item in items), Decimal("0.00"))

    return Order(
        user_id=user_id,
        status="pending",
        total_amount=total,
        shipping_recipient_name=shipping.recipient_name,
        shipping_phone=shipping.phone,
        shipping_line1=shipping.line1,
        shipping_line2=shipping.line2,
        shipping_city=shipping.city,
        shipping_region=shipping.region,
        shipping_postal_code=shipping.postal_code,
        shipping_country=shipping.country,
        items=items,
    )


def _must_be_buyable(product: Product, quantity: int) -> None:
    """Refuse a product that is off sale, or more of it than exists.

    The cart has a check that looks like this one, and they are not the
    same check. The cart's is a courtesy, run against an unlocked row so
    the customer hears about an obvious problem early; it guarantees
    nothing, because another customer can take the last one a moment
    later. This one runs against a locked row inside the order
    transaction, and it is the one that decides. Sharing them would hide
    that difference.
    """
    if not product.is_active:
        raise UnavailableError(f"{product.name} is no longer on sale")
    if quantity > product.stock_quantity:
        raise UnavailableError(
            f"Only {product.stock_quantity} of {product.name} are left, and you asked for "
            f"{quantity}"
        )


def checkout(db: Session, user_id: int, address_id: int, expected_total: Decimal) -> Order:
    """Turn the caller's cart into an order, or change nothing at all.

    The sequence is fixed and the order of its steps is the whole point:

        lock the cart, so the customer cannot change it underneath us
        read its lines, without their products
        refuse an empty cart
        snapshot the address, scoped to this customer
        lock the products, sorted by id
        check and copy from the LOCKED rows
        refuse if the total is not what the customer was shown
        write the order, take the stock, clear the cart
        commit

    Nothing is durable until that last line. If any step raises, the
    rollback below releases every lock and leaves the database exactly as
    it was - no half-order, no stock taken for goods nobody bought.

    Payment is deliberately not here. The order is created as 'pending'
    with no provider call inside the transaction, because a three-second
    payment round trip holding a product's row lock queues every other
    customer buying that product behind it (Step 44).
    """
    try:
        cart_id = cart_repo.get_cart_id(db, user_id)
        if cart_id is None:
            raise EmptyCartError("Your cart is empty")

        # Taken before the lines are read. Reading first and locking after
        # is how Step 37's lock ended up protecting nothing.
        cart_repo.lock_cart(db, cart_id)

        lines = cart_repo.get_items(db, cart_id)
        if not lines:
            raise EmptyCartError("Your cart is empty")

        # Before the product locks, so a bad address id fails early rather
        # than after holding locks. Resolved through the ownership-scoped
        # lookup, so an id belonging to someone else is a 404 here exactly
        # as it is everywhere else.
        shipping = address_service.snapshot_for_shipping(db, user_id, address_id)

        products = product_repo.lock_many(db, (line.product_id for line in lines))

        # Only now are the values trustworthy. Everything the cart reported
        # was read without a lock and may since have changed.
        ordered: list[tuple[Product, int]] = []
        for line in lines:
            product = products.get(line.product_id)
            if product is None:
                raise NotFoundError(f"Product {line.product_id} does not exist")
            _must_be_buyable(product, line.quantity)
            ordered.append((product, line.quantity))

        order = build_order(user_id, shipping, ordered)

        # The last gate before anything is written. The prices above came
        # from locked rows and may differ from the ones the customer was
        # shown, so charging without asking would take an amount they never
        # agreed to. Only the totals can be compared - the cart stores no
        # per-line price, so the message cannot honestly say which product
        # moved.
        if order.total_amount != expected_total:
            raise PriceChangedError(
                f"The total is now {order.total_amount}, not {expected_total}. "
                f"Check your cart and try again."
            )

        repo.add(db, order)

        for product, quantity in ordered:
            product.stock_quantity -= quantity

        # Inside the transaction, not after it. A separate clearing
        # transaction would leave a window in which the order exists and
        # the cart still does, and a refresh in that window orders twice.
        cart_repo.clear_items(db, cart_id)

        db.commit()
        return order
    except Exception:
        # Any failure releases the cart and product locks immediately
        # rather than holding them until the request ends.
        db.rollback()
        raise
