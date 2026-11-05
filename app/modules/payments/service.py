"""Business rules for payments. The only layer here that commits.

The rule this module exists to keep: the shop never decides that a payment
succeeded. It records what the provider says, after checking the provider
really said it.
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AlreadyExistsError,
    BusyError,
    InvalidTransitionError,
    NotFoundError,
)
from app.modules.orders import service as order_service
from app.modules.payments import repository as repo
from app.modules.payments.models import Payment, PaymentStatus, WebhookEvent
from app.modules.payments.provider import PaymentIntent, get_provider

LOCK_TIMEOUT = "5s"

# Which payment status may follow which. Everything not listed is ignored
# rather than refused, because webhooks are retried and reordered: a
# 'succeeded' event arriving after a refund is not an error, it is an old
# delivery, and the right response is to do nothing and say so.
ALLOWED_PAYMENT_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"succeeded", "failed"}),
    "succeeded": frozenset({"refunded"}),
    "failed": frozenset(),
    "refunded": frozenset(),
}

# What each event type means for the payment it names. An event type that
# is not here is recorded and otherwise ignored.
EVENT_TO_STATUS: dict[str, PaymentStatus] = {
    "payment.succeeded": "succeeded",
    "payment.failed": "failed",
    "refund.succeeded": "refunded",
}

# Adding a status to one map and forgetting the other would fail on a real
# event, in production. Checked at import, so the application refuses to
# start instead.
assert set(EVENT_TO_STATUS.values()) <= set(ALLOWED_PAYMENT_TRANSITIONS), (
    "every event maps to a status that has transition rules"
)


def _bound_lock_wait(db: Session) -> None:
    """Stop this transaction waiting forever for a row lock."""
    db.execute(text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))


def start_payment(db: Session, user_id: int, order_id: int) -> tuple[Payment, PaymentIntent]:
    """Begin paying for one of this customer's own orders.

    Returns a pending payment and the provider's instructions. Nothing here
    means the order is paid: that only happens when a signed webhook says
    so.

    The provider call happens outside any row lock, for the reason measured
    in Step 44 - a three-second round trip inside a lock queues every other
    customer behind it.
    """
    settings = get_settings()
    provider = get_provider()

    # Ownership-scoped, so an order belonging to someone else is a 404 here
    # exactly as it is everywhere else.
    order = order_service.get_order(db, user_id, order_id)
    if order.status != "pending":
        raise InvalidTransitionError(f"An order that is {order.status} cannot be paid for")
    if repo.succeeded_for_order(db, order_id) is not None:
        raise AlreadyExistsError(f"Order {order_id} has already been paid")

    intent = provider.create_payment(order.id, order.total_amount, settings.payment_currency)

    try:
        payment = Payment(
            order_id=order.id,
            provider=provider.name,
            reference=intent.reference,
            # Copied from the order now, so the record says what was asked
            # for even if the order is somehow changed later.
            amount=order.total_amount,
            currency=settings.payment_currency,
            status="pending",
        )
        repo.add(db, payment)
        db.commit()
        return payment, intent
    except Exception:
        db.rollback()
        raise


def list_payments(db: Session, user_id: int, order_id: int) -> list[Payment]:
    """Every payment attempt against one of this customer's orders."""
    order = order_service.get_order(db, user_id, order_id)
    return repo.list_for_order(db, order.id)


def start_refund(db: Session, order_id: int) -> Payment:
    """Ask the provider to send the money back.

    The payment is NOT marked refunded here and the order is not cancelled.
    Both wait for a refund.succeeded event, because a refund that was
    requested and a refund that happened are different facts and only one
    of them belongs in a financial record.

    No user_id argument: refunding is an operator action, and the router is
    what checks the caller is an admin.
    """
    payment = repo.succeeded_for_order(db, order_id)
    if payment is None:
        raise NotFoundError(f"Order {order_id} has no successful payment to refund")

    get_provider().start_refund(payment.reference, payment.amount)
    return payment


def handle_webhook(db: Session, provider_name: str, raw_body: bytes, signature: str) -> str:
    """Apply one provider event, exactly once.

    Returns a word describing what happened, for the caller to log:
    'applied', 'duplicate' or 'ignored'.

    The order of operations is the point:

      1. check the signature, before parsing anything
      2. record the event id - a duplicate fails here
      3. lock the payment row
      4. apply only if the move is legal from where it is now
      5. commit, so the effect and the record of having seen the event are
         inseparable

    Step 2 sharing a transaction with step 4 is what makes delivery twice
    safe. Recorded separately, a crash between them would leave an event
    marked seen but never applied, or applied twice.
    """
    provider = get_provider()
    if provider_name != provider.name:
        raise NotFoundError(f"No payment provider named {provider_name}")

    # Raises ValidationError on a bad signature or an unparseable body,
    # before anything touches the database.
    event = provider.read_webhook(raw_body, signature)

    try:
        _bound_lock_wait(db)

        seen = WebhookEvent(
            provider=provider.name,
            event_id=event.event_id,
            event_type=event.event_type,
        )
        try:
            repo.add(db, seen)
        except IntegrityError:
            # Seen before. Providers retry; this is normal traffic rather
            # than an error, and the caller answers 200 so they stop.
            db.rollback()
            return "duplicate"

        new_status = EVENT_TO_STATUS.get(event.event_type)
        if new_status is None:
            # An event type this shop does not act on. The id is still
            # recorded, so a redelivery is recognised as a duplicate.
            db.commit()
            return "ignored"

        payment = repo.get_by_reference_for_update(db, provider.name, event.reference)
        if payment is None:
            raise NotFoundError(f"No payment with reference {event.reference}")

        if new_status not in ALLOWED_PAYMENT_TRANSITIONS[payment.status]:
            # Out of order, or stale. A 'failed' arriving after 'succeeded'
            # must not un-pay the order. The commit keeps the event id, so
            # a later redelivery is a duplicate rather than a fresh attempt.
            db.commit()
            return "ignored"

        payment.status = new_status
        _apply_to_order(db, payment, new_status)

        db.commit()
        return "applied"
    except OperationalError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "55P03":
            raise BusyError("Busy. Please deliver this event again.") from exc
        raise
    except Exception:
        db.rollback()
        raise


def _apply_to_order(db: Session, payment: Payment, new_status: str) -> None:
    """Move the order to match what just happened to its payment."""
    order = order_service.lock_order(db, payment.order_id)
    if order is None:
        raise NotFoundError(f"Order {payment.order_id} does not exist")

    # Only from pending. An order cancelled before the money arrived must
    # not quietly become paid: that is a refund to arrange, not a state to
    # overwrite.
    if new_status == "succeeded" and order.status == "pending":
        order.status = "paid"

    # The money is back, so the goods are ours again. Both halves in one
    # transaction, so stock and order status cannot disagree.
    elif new_status == "refunded" and order.status in {"pending", "paid"}:
        order_service.return_stock(db, order)
        order.status = "cancelled"

    # 'failed' changes nothing about the order. It stays pending, the
    # customer may try again, and the failed attempt stays on record.
