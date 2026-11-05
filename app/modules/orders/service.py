"""Business rules for orders. The only layer that commits.

This module owns the one thing that makes an order a record rather than a
view: the moment the product's details stop being looked up and start being
copied. Checkout is the transaction around that moment.
"""

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusyError,
    EmptyCartError,
    InvalidTransitionError,
    NotFoundError,
    PriceChangedError,
    UnavailableError,
)
from app.modules.addresses import service as address_service
from app.modules.addresses.schemas import ShippingAddress
from app.modules.cart import repository as cart_repo
from app.modules.orders import repository as repo
from app.modules.orders.models import ORDER_STATUSES, Order, OrderItem, OrderStatus
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


# Which status an order may move to, from the one it has. Everything not
# listed is refused.
#
# This lives in the service, not in models.py beside the status values,
# because the database is not what enforces it. A check constraint can say
# the status is one of five words; it cannot say that a delivered order
# must not become pending again, because that depends on the row's previous
# value. Putting the map here keeps the rule next to the code that applies
# it.
#
# delivered and cancelled are terminal. A delivered order that comes back
# is a return, which is a new record rather than an edit to this one, and a
# cancelled order that is reinstated is a new order. Both are deliberate
# gaps rather than oversights.
#
# shipped cannot be cancelled: once a parcel is with a courier, stopping it
# is a return, not a cancellation, and pretending otherwise would put the
# order in a state that does not match where the goods actually are.
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"paid", "cancelled"}),
    "paid": frozenset({"shipped", "cancelled"}),
    "shipped": frozenset({"delivered"}),
    "delivered": frozenset(),
    "cancelled": frozenset(),
}

# Adding a status to OrderStatus and forgetting it here would raise KeyError
# on a real order, in production, the first time one reached that status.
# Checked at import instead, so the application refuses to start.
assert set(ALLOWED_TRANSITIONS) == set(ORDER_STATUSES), (
    "every order status needs an entry in ALLOWED_TRANSITIONS"
)


# How long checkout waits for any one row lock before giving up. A plain
# constant rather than a setting: it is a property of this transaction, not
# something an operator should tune per environment without understanding
# what it protects.
LOCK_TIMEOUT = "5s"


def _bound_lock_wait(db: Session) -> None:
    """Stop this transaction waiting forever for a row lock.

    SET LOCAL applies to this transaction only, so it cannot leak to
    whatever else borrows this pooled connection next.

    Without it a statement waits for a row lock indefinitely. Checkout
    holds a cart lock and several product locks at once, so one stuck
    transaction on a popular product would queue every other customer
    buying it, each holding a pooled connection until the pool is empty and
    endpoints with nothing to do with orders start failing. Five seconds is
    far longer than a healthy checkout needs - twenty of them contending
    over the same two products measured at tens of milliseconds each - so
    reaching it means something is wrong, and failing fast is better than
    queueing.
    """
    db.execute(text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))


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


def checkout(
    db: Session,
    user_id: int,
    address_id: int,
    expected_total: Decimal,
    idempotency_key: str | None = None,
) -> tuple[Order, bool]:
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

    Returns the order and whether it was created now. With an
    idempotency_key, a repeat of a request that already succeeded returns
    that same order and False, instead of making a second one.
    """
    if idempotency_key is not None:
        # Checked before any lock is taken. A retry of something that
        # already finished should cost nothing and block nobody.
        existing = repo.order_for_key(db, user_id, idempotency_key)
        if existing is not None:
            return existing, False

    try:
        _bound_lock_wait(db)

        cart_id = cart_repo.get_cart_id(db, user_id)
        if cart_id is None:
            raise EmptyCartError("Your cart is empty")

        # Taken before the lines are read. Reading first and locking after
        # is how Step 37's lock ended up protecting nothing.
        cart_repo.lock_cart(db, cart_id)

        if idempotency_key is not None:
            # Checked again, now that the cart lock has serialised this
            # request behind any duplicate of it. The check before the lock
            # ran too early to see a twin that was still in flight: that
            # one then committed, cleared the cart, and this request would
            # have reported an empty cart - the confusing answer the key
            # exists to prevent.
            existing = repo.order_for_key(db, user_id, idempotency_key)
            if existing is not None:
                db.rollback()
                return existing, False

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

        if idempotency_key is not None:
            # Inside the transaction, so the key and the order commit
            # together. A checkout that fails leaves no key behind, which
            # is what makes retrying a failure safe.
            #
            # A concurrent duplicate reaches this INSERT while the first
            # transaction still holds the unique index entry, waits, and
            # then fails once that commits. The database decides, not a
            # check that could race.
            try:
                repo.claim_idempotency_key(db, user_id, idempotency_key, order.id)
            except IntegrityError:
                db.rollback()
                first = repo.order_for_key(db, user_id, idempotency_key)
                if first is None:
                    raise
                return first, False

        db.commit()
        return order, True
    except OperationalError as exc:
        db.rollback()
        # 55P03 is lock_not_available: a row lock was held by someone else
        # for longer than lock_timeout. Translated here so the router never
        # sees a database error, and so the client is told to try again
        # rather than which rows were busy.
        if getattr(exc.orig, "sqlstate", None) == "55P03":
            raise BusyError("The shop is busy right now. Please try again.") from exc
        raise
    except Exception:
        # Any failure releases the cart and product locks immediately
        # rather than holding them until the request ends.
        db.rollback()
        raise


def change_status(db: Session, order_id: int, new_status: OrderStatus) -> Order:
    """Move an order to a new status, or refuse and change nothing.

    The order is locked before its current status is read. A status change
    is a read-modify-write - look at where it is, decide, write where it
    goes - which races exactly as stock did in Step 34. Without the lock, a
    payment and a cancellation arriving together could both read 'pending',
    both find their move legal, and the second would silently overwrite the
    first.

    Staying put is refused along with everything else. Asking a paid order
    to become paid is not harmless: it means the caller believed it was in
    some other state, and quietly agreeing hides that.

    Taking stock back when an order is cancelled is NOT done here. It is a
    business decision with its own rules - whether a cancelled paid order
    returns stock immediately or after a refund clears - and it belongs
    with the cancellation endpoint in Step 51.
    """
    try:
        order = repo.get_by_id_for_update(db, order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} does not exist")

        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise InvalidTransitionError(
                f"An order that is {order.status} cannot become {new_status}"
            )

        order.status = new_status
        db.commit()
        return order
    except Exception:
        db.rollback()
        raise


def lock_order(db: Session, order_id: int) -> Order | None:
    """Lock one order's row, whoever it belongs to.

    No user_id: this is for callers not acting on behalf of a customer,
    such as applying a payment event. Ownership checks belong to the paths
    that have a customer to check against.
    """
    return repo.get_by_id_for_update(db, order_id)


def return_stock(db: Session, order: Order) -> None:
    """Put an order's goods back on the shelf. The caller commits.

    Used by customer cancellation and by a confirmed refund, so the two
    agree by construction rather than by two similar loops staying in step.

    Sorted inside lock_many, as in checkout, so returning stock and selling
    it cannot deadlock.
    """
    products = product_repo.lock_many(db, (item.product_id for item in order.items))
    for item in order.items:
        product = products.get(item.product_id)
        if product is not None:
            product.stock_quantity += item.quantity


def list_orders(db: Session, user_id: int) -> Sequence[Order]:
    """Every order this customer placed, newest first."""
    return repo.list_for_user(db, user_id)


def get_order(db: Session, user_id: int, order_id: int) -> Order:
    """One of this customer's orders.

    An order belonging to someone else raises NotFoundError, the same as
    one that does not exist. A 403 would confirm that the id is real, which
    is a slow way of listing every order in the shop.
    """
    order = repo.get_for_user(db, user_id, order_id)
    if order is None:
        raise NotFoundError(f"Order {order_id} does not exist")
    return order


def cancel_order(db: Session, user_id: int, order_id: int) -> Order:
    """Cancel one of this customer's own orders and put the stock back.

    Only from 'pending'. A paid order involves money that has already
    moved, so cancelling it is a refund workflow with a provider in it -
    Step 58 - and not something a customer can do by calling an endpoint.
    The state machine allows paid -> cancelled; this path deliberately does
    not use that freedom.

    Returning the stock is the half that Step 49 left out. It happens in
    the same transaction as the status change, so the shelf and the order
    can never disagree: either both happened or neither did.
    """
    try:
        _bound_lock_wait(db)

        # Locked first, and the ownership check comes from the locked row.
        # Reading it unlocked and then locking would leave a gap in which
        # the status could change underneath the decision.
        order = repo.get_by_id_for_update(db, order_id)
        if order is None or order.user_id != user_id:
            raise NotFoundError(f"Order {order_id} does not exist")

        if order.status != "pending":
            raise InvalidTransitionError(
                f"An order that is {order.status} cannot be cancelled here"
            )

        return_stock(db, order)

        order.status = "cancelled"
        db.commit()
        return order
    except OperationalError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "55P03":
            raise BusyError("The shop is busy right now. Please try again.") from exc
        raise
    except Exception:
        db.rollback()
        raise
