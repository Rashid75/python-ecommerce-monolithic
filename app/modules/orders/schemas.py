"""What checkout accepts, and what an order looks like on the way out.

The request contract and the read shapes. The statuses themselves live in
models.py, beside the check constraint that enforces them, so that they
are written down once rather than twice.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.modules.addresses.schemas import ShippingAddress
from app.modules.orders.models import OrderStatus

if TYPE_CHECKING:
    from app.modules.orders.models import Order


class CheckoutRequest(BaseModel):
    """Everything a client may say about an order. It is almost nothing.

    No items, no quantities, no prices, no total, no user. Each of those
    already exists on the server - the cart rows, products.price, the
    arithmetic, and the token - and a field a client can send is a field an
    attacker can set.

    address_id is the one exception, and it is safe only because it is
    resolved against that customer's own addresses: an id belonging to
    someone else does not match, so it cannot be used to post a parcel to
    an address the caller cannot already see.
    """

    model_config = ConfigDict(extra="forbid")

    address_id: int = Field(gt=0)


class OrderItemRead(BaseModel):
    """One line of an order, exactly as it was bought.

    Every field here is the snapshot, not the live product. product_id is
    carried so a client can link back to the catalogue page, but nothing
    on this line is read from it.
    """

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    name: str
    unit_price: Decimal
    quantity: int

    @computed_field
    @property
    def line_total(self) -> Decimal:
        """unit_price x quantity.

        Computed rather than stored, unlike the order's total_amount. The
        inputs are both frozen snapshots, so this can only ever give the
        same answer - there is no history to lose. The order's total is
        different: it is what was charged, which must not be recomputed.
        """
        return self.unit_price * self.quantity


class OrderRead(BaseModel):
    """An order as a customer sees it.

    No user_id: the caller is the owner, and repeating their id tells them
    nothing they do not know while handing an attacker a number to try.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    total_amount: Decimal
    shipping: ShippingAddress
    items: list[OrderItemRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_order(cls, order: "Order") -> "OrderRead":
        """Build the response from an Order row.

        Written out by hand because the eight shipping columns are flat on
        the table - shipping_city and so on - while the API nests them
        under one shipping object. Something has to bridge the two, and an
        explicit function is easier to follow than a validator that
        rearranges fields invisibly.
        """
        return cls(
            id=order.id,
            status=order.status,
            total_amount=order.total_amount,
            shipping=ShippingAddress(
                recipient_name=order.shipping_recipient_name,
                phone=order.shipping_phone,
                line1=order.shipping_line1,
                line2=order.shipping_line2,
                city=order.shipping_city,
                region=order.shipping_region,
                postal_code=order.shipping_postal_code,
                country=order.shipping_country,
            ),
            items=[OrderItemRead.model_validate(item) for item in order.items],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
