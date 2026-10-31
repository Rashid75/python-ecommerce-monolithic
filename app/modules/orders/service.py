"""Business rules for orders.

This module owns the one thing that makes an order a record rather than a
view: the moment the product's details stop being looked up and start being
copied.
"""

from collections.abc import Sequence
from decimal import Decimal

from app.modules.addresses.schemas import ShippingAddress
from app.modules.orders.models import Order, OrderItem
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
