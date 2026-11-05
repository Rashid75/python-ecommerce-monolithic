"""HTTP endpoints for orders.

No user id appears in any path. An order is always reached through the
authenticated caller, and the ownership check lives in the WHERE clause of
the query rather than in an `if` after the row is already in hand.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Response, status

from app.db.session import DbSession
from app.modules.orders import service
from app.modules.orders.schemas import CheckoutRequest, OrderRead
from app.modules.users.dependencies import CurrentUser

router = APIRouter(prefix="/orders", tags=["orders"])

# An optional header rather than a body field: it describes the request
# attempt, not the order. Two attempts at the same order differ in their
# key while the body stays identical, which is exactly the distinction.
IdempotencyKey = Annotated[
    str | None,
    Header(
        alias="Idempotency-Key",
        max_length=64,
        description="Send the same key when retrying, to avoid ordering twice.",
    ),
]


# 201, unlike the cart's 200s: this creates a record that did not exist and
# will never be replaced by a later request.
@router.post("", status_code=status.HTTP_201_CREATED, summary="Check out my cart")
def checkout(
    data: CheckoutRequest,
    user: CurrentUser,
    db: DbSession,
    response: Response,
    idempotency_key: IdempotencyKey = None,
) -> OrderRead:
    order, created = service.checkout(
        db, user.id, data.address_id, data.expected_total, idempotency_key
    )
    if not created:
        # Still 201, because that is the response the first attempt got and
        # a replay returns the original answer. The header says it was a
        # replay for anyone who needs to tell the difference.
        response.headers["Idempotent-Replay"] = "true"
    return OrderRead.from_order(order)


@router.get("", summary="List my orders")
def list_orders(user: CurrentUser, db: DbSession) -> list[OrderRead]:
    return [OrderRead.from_order(order) for order in service.list_orders(db, user.id)]


@router.get("/{order_id}", summary="Get one of my orders")
def get_order(order_id: int, user: CurrentUser, db: DbSession) -> OrderRead:
    order = service.get_order(db, user.id, order_id)
    return OrderRead.from_order(order)


# POST .../cancellation rather than DELETE /orders/{id}. Nothing is deleted:
# a cancellation is a new fact recorded on an order that goes on existing,
# which is the whole point of an order being a record.
@router.post("/{order_id}/cancellation", summary="Cancel one of my orders")
def cancel_order(order_id: int, user: CurrentUser, db: DbSession) -> OrderRead:
    order = service.cancel_order(db, user.id, order_id)
    return OrderRead.from_order(order)
