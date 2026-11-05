"""HTTP endpoints for payments, and the provider's webhook.

Two very different kinds of endpoint live here. The customer-facing ones
are authenticated with a token and scoped to the caller's own orders. The
webhook is called by a machine that has no token at all, and is trusted
only because of a signature over the exact bytes it sent.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Request, status
from fastapi.concurrency import run_in_threadpool

from app.db.session import DbSession
from app.modules.payments import service
from app.modules.payments.schemas import PaymentRead, PaymentStarted
from app.modules.users.dependencies import AdminUser, CurrentUser

router = APIRouter(tags=["payments"])


@router.post(
    "/orders/{order_id}/payments",
    status_code=status.HTTP_201_CREATED,
    summary="Start paying for one of my orders",
)
def start_payment(order_id: int, user: CurrentUser, db: DbSession) -> PaymentStarted:
    payment, intent = service.start_payment(db, user.id, order_id)
    return PaymentStarted(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        created_at=payment.created_at,
        instructions=intent.instructions,
    )


@router.get("/orders/{order_id}/payments", summary="Payment attempts on one of my orders")
def list_payments(order_id: int, user: CurrentUser, db: DbSession) -> list[PaymentRead]:
    payments = service.list_payments(db, user.id, order_id)
    return [PaymentRead.model_validate(payment) for payment in payments]


# Admin only. A customer cannot refund themselves, and AdminUser is what
# enforces it - a dependency rather than a check inside the handler that
# could be forgotten on the next endpoint.
@router.post("/orders/{order_id}/refunds", summary="Ask the provider to refund an order")
def start_refund(order_id: int, admin: AdminUser, db: DbSession) -> PaymentRead:
    payment = service.start_refund(db, order_id)
    # Still 'succeeded'. The refund has been asked for, not confirmed, and
    # the status will only change when the provider says it has happened.
    return PaymentRead.model_validate(payment)


Signature = Annotated[str | None, Header(alias="X-Signature")]


# async, unlike every other endpoint here, and for one reason: the raw
# request body. A signature covers exactly the bytes that were sent, and
# letting FastAPI parse the JSON into a model would mean re-serialising it
# to check - which changes key order and whitespace, so the signature would
# never match. request.body() gives the bytes as sent, and reading it is
# awaitable.
#
# The database work is then handed to a worker thread. SQLAlchemy here is
# synchronous, and calling it directly inside an async function would block
# the event loop for the whole transaction, stalling every other request
# the process is serving.
@router.post("/webhooks/{provider_name}", summary="Receive a payment provider event")
async def receive_webhook(
    provider_name: str, request: Request, db: DbSession, x_signature: Signature = None
) -> dict[str, str]:
    payload = await request.body()
    outcome = await run_in_threadpool(
        service.handle_webhook, db, provider_name, payload, x_signature or ""
    )
    # 200 for applied, duplicate and ignored alike. Anything else makes the
    # provider retry an event that has already been dealt with.
    return {"status": outcome}
