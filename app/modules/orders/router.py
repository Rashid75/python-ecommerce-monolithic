"""HTTP endpoints for orders.

No user id and no cart id appears in any path. The order is always built
from the caller's own cart, taken from the authenticated token, so there is
nothing in the request a client could change to reach someone else's.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import (
    EmptyCartError,
    NotFoundError,
    PriceChangedError,
    UnavailableError,
)
from app.db.session import DbSession
from app.modules.orders import service
from app.modules.orders.schemas import CheckoutRequest, OrderRead
from app.modules.users.dependencies import CurrentUser

router = APIRouter(prefix="/orders", tags=["orders"])


# 201, unlike the cart's 200s: this creates a record that did not exist and
# will never be replaced by a later request.
@router.post("", status_code=status.HTTP_201_CREATED, summary="Check out my cart")
def checkout(data: CheckoutRequest, user: CurrentUser, db: DbSession) -> OrderRead:
    try:
        order = service.checkout(db, user.id, data.address_id, data.expected_total)
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
    return OrderRead.from_order(order)
