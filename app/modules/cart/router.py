"""HTTP endpoints for the cart.

No cart id appears in any path. The cart is always the caller's own, taken
from the authenticated token, so there is no identifier for a client to
change to someone else's.
"""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import NotFoundError, UnavailableError, ValidationError
from app.db.session import DbSession
from app.modules.cart import service
from app.modules.cart.models import Cart
from app.modules.cart.schemas import (
    CartItemAdd,
    CartItemRead,
    CartItemSetQuantity,
    CartRead,
)
from app.modules.users.dependencies import CurrentUser

router = APIRouter(prefix="/cart", tags=["cart"])


def _to_read(cart: Cart) -> CartRead:
    """Assemble the response from the cart lines and their products.

    The quantity comes from cart_items and everything else from products,
    read now rather than copied when the item was added.
    """
    items = [
        CartItemRead(
            product_id=item.product_id,
            sku=item.product.sku,
            name=item.product.name,
            quantity=item.quantity,
            unit_price=item.product.price,
            line_total=item.product.price * item.quantity,
            is_active=item.product.is_active,
            available_stock=item.product.stock_quantity,
            issue=service.line_issue(item),
        )
        for item in cart.items
    ]
    return CartRead(
        items=items,
        total_items=sum(item.quantity for item in items),
        # Decimal("0") as the start value, so an empty cart totals Decimal
        # rather than int and the type stays consistent.
        total=sum((item.line_total for item in items), Decimal("0")),
        has_issues=any(item.issue is not None for item in items),
    )


@router.get("", summary="Get my cart")
def get_cart(user: CurrentUser, db: DbSession) -> CartRead:
    # An empty cart, not a 404: every signed-in customer has one.
    return _to_read(service.get_cart(db, user.id))


# 200, not 201. The response is the whole cart, the request may increase an
# existing line rather than create one, and there is no new URL to point at.
@router.post("/items", summary="Add a product to my cart")
def add_item(data: CartItemAdd, user: CurrentUser, db: DbSession) -> CartRead:
    try:
        cart = service.add_item(db, user.id, data.product_id, data.quantity)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except UnavailableError as exc:
        # 409, not 422: the request is well formed and the product exists.
        # It conflicts with the product's current state.
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return _to_read(cart)


# PUT, not PATCH: the line has one mutable field, so sending the quantity
# replaces the whole of it. It is also idempotent - sending the same request
# twice leaves the same result, which a retrying client can rely on.
@router.put("/items/{product_id}", summary="Set the quantity of an item in my cart")
def set_item_quantity(
    product_id: int, data: CartItemSetQuantity, user: CurrentUser, db: DbSession
) -> CartRead:
    try:
        cart = service.set_item_quantity(db, user.id, product_id, data.quantity)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except UnavailableError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return _to_read(cart)


# Returns the cart rather than 204. Removing a line changes the total, and
# the client needs the new one; a bare 204 would force an immediate GET.
@router.delete("/items/{product_id}", summary="Remove an item from my cart")
def remove_item(product_id: int, user: CurrentUser, db: DbSession) -> CartRead:
    try:
        cart = service.remove_item(db, user.id, product_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return _to_read(cart)


# 204 here, unlike the line delete above: the result of emptying a cart is
# known in advance, so there is nothing worth sending back.
@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Empty my cart")
def clear_cart(user: CurrentUser, db: DbSession) -> None:
    service.clear_cart(db, user.id)
