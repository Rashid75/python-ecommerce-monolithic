"""HTTP endpoints for the cart.

No cart id appears in any path. The cart is always the caller's own, taken
from the authenticated token, so there is no identifier for a client to
change to someone else's.
"""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import DbSession
from app.modules.cart import service
from app.modules.cart.models import Cart
from app.modules.cart.schemas import CartItemAdd, CartItemRead, CartRead
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
        )
        for item in cart.items
    ]
    return CartRead(
        items=items,
        total_items=sum(item.quantity for item in items),
        # Decimal("0") as the start value, so an empty cart totals Decimal
        # rather than int and the type stays consistent.
        total=sum((item.line_total for item in items), Decimal("0")),
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
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return _to_read(cart)
