"""What the cart API accepts and returns.

A cart line is assembled from two tables - the quantity from cart_items and
everything else from products - so these schemas are built explicitly
rather than read straight off one ORM object.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# An upper bound on a single add. Not a business rule so much as a guard:
# quantity is a PostgreSQL integer, and repeated unbounded adds would
# eventually overflow it. A real shop would set this per product.
MAX_QUANTITY = 999


class CartItemAdd(BaseModel):
    """Add a product to the cart, or add more of one already in it."""

    # Unknown keys are rejected rather than ignored, for the reason found in
    # Step 33: a silently dropped field looks like success to the client.
    model_config = ConfigDict(extra="forbid")

    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=MAX_QUANTITY)


class CartItemSetQuantity(BaseModel):
    """Set a cart line to an exact quantity.

    Absolute, unlike the stock adjustments in Step 33, and for a reason
    rather than by accident. Stock is shared: setting it to a number means
    "I believe it is 4, make it 3", and that belief can already be wrong.
    A cart belongs to one person, so "I want 3" is a fact about their
    intent, not an inference about state someone else may have changed.

    Zero is rejected rather than treated as removal. Emptying a line is a
    different operation and has its own endpoint, and quantity > 0 is what
    the database enforces anyway.
    """

    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1, le=MAX_QUANTITY)


class CartItemRead(BaseModel):
    """One line of the cart.

    The product is identified by product_id, not by the cart_items row id.
    The row id is an internal detail, and a client that never sees it can
    never ask for someone else's.
    """

    product_id: int
    sku: str
    name: str
    quantity: int
    # The product's price right now, not a copy taken when the item was
    # added. Decimal throughout: money is never a float.
    unit_price: Decimal
    line_total: Decimal


class CartRead(BaseModel):
    """The whole cart. There is no id here either - it is always yours."""

    items: list[CartItemRead]
    total_items: int
    total: Decimal
