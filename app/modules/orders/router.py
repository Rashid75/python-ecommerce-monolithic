"""HTTP endpoints for orders.

No user id appears in any path. An order is always reached through the
authenticated caller, and the ownership check lives in the WHERE clause of
the query rather than in an `if` after the row is already in hand.
"""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from app.core.exceptions import (
    BusyError,
    EmptyCartError,
    InvalidTransitionError,
    NotFoundError,
    PriceChangedError,
    UnavailableError,
)
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
    try:
        order, created = service.checkout(
            db, user.id, data.address_id, data.expected_total, idempotency_key
        )
    except EmptyCartError as exc:
        # 409: the cart exists and the request is well formed. It conflicts
        # with the state of the cart.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except NotFoundError as exc:
        # The address is not this customer's, or does not exist. The same
        # 404 for both, so the response cannot be used to discover which
        # address ids are real.
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except PriceChangedError as exc:
        # 409 as well, and deliberately not a silent re-price. The customer
        # is shown the new total and decides again.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except UnavailableError as exc:
        # Sold out or withdrawn between adding to the cart and checking
        # out. 409 rather than 422: nothing about the request was wrong.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except BusyError as exc:
        # 503, not 500: nothing is broken and the request was valid. The
        # message says to try again and nothing about what was locked.
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

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
    try:
        order = service.get_order(db, user.id, order_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return OrderRead.from_order(order)


# POST .../cancellation rather than DELETE /orders/{id}. Nothing is deleted:
# a cancellation is a new fact recorded on an order that goes on existing,
# which is the whole point of an order being a record.
@router.post("/{order_id}/cancellation", summary="Cancel one of my orders")
def cancel_order(order_id: int, user: CurrentUser, db: DbSession) -> OrderRead:
    try:
        order = service.cancel_order(db, user.id, order_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except InvalidTransitionError as exc:
        # 409: the order exists and is the caller's, but is past the point
        # where cancelling is something they can do alone.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except BusyError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    return OrderRead.from_order(order)
