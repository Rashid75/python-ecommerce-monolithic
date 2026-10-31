"""The orders and order_items tables.

An order is a record, not working state. Everything before Phase 9 could be
edited or thrown away - a cart is emptied, an address is corrected, a price
changes tomorrow. An order must still read correctly in five years, so it
copies what it needs instead of pointing at it, and nothing here is meant
to be updated afterwards except the status.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, get_args

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# The statuses an order may have. Which moves between them are allowed is
# Step 49; this is only the set of legal values.
OrderStatus = Literal["pending", "paid", "shipped", "delivered", "cancelled"]

# The same values as a plain tuple. get_args reads them back off the type
# above, so the check constraint and the API type cannot drift apart.
ORDER_STATUSES: tuple[str, ...] = get_args(OrderStatus)

_STATUS_SQL_LIST = ", ".join(f"'{status}'" for status in ORDER_STATUSES)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ondelete="RESTRICT", the opposite of carts and addresses. Those
    # CASCADE because they are the customer's working state and have no
    # meaning without them. An order is a financial record: deleting the
    # customer must not take it, so PostgreSQL refuses to delete a user who
    # has ordered anything.
    #
    # index=True because "my orders" filters on it and PostgreSQL does not
    # index a foreign key for you.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)

    # No server_default. Whoever creates an order says what state it is in,
    # rather than relying on a default that is invisible from the calling
    # code. The check constraint below is what makes a typo impossible.
    status: Mapped[OrderStatus] = mapped_column(String(20))

    # What was actually charged - a fact about money that moved, not a
    # calculation to redo on every read. Recomputing it from the lines
    # would let a future change to the arithmetic silently rewrite history.
    # Numeric, never Float, for the reason in products.price.
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # The shipping address as a copy, frozen at checkout. Eight flat
    # columns rather than a foreign key to addresses, because the customer
    # may edit or delete that row and the order must still say where the
    # parcel went. Flat rather than JSON so the columns can be indexed,
    # constrained and read in psql without JSON operators.
    #
    # Nullable here exactly where it is nullable on Address.
    shipping_recipient_name: Mapped[str] = mapped_column(String(200))
    shipping_phone: Mapped[str] = mapped_column(String(30))
    shipping_line1: Mapped[str] = mapped_column(String(200))
    shipping_line2: Mapped[str | None] = mapped_column(String(200), default=None)
    shipping_city: Mapped[str] = mapped_column(String(100))
    shipping_region: Mapped[str | None] = mapped_column(String(100), default=None)
    shipping_postal_code: Mapped[str | None] = mapped_column(String(20), default=None)
    shipping_country: Mapped[str] = mapped_column(String(2))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # No cascade="all, delete-orphan", unlike Cart.items. Removing a line
    # from an order is not a thing that should happen, so the ORM is given
    # no way to do it quietly: deleting an Order through the session would
    # try to null the children's order_id and fail loudly on NOT NULL.
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", order_by="OrderItem.id")

    __table_args__ = (
        CheckConstraint(f"status IN ({_STATUS_SQL_LIST})", name="status_is_known"),
        CheckConstraint("total_amount >= 0", name="total_not_negative"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    # CASCADE: a line has no meaning without its order. Orders are not
    # deleted in normal operation, so this is a tidiness rule rather than a
    # workflow - and the missing ORM cascade above means the application
    # cannot trigger it by accident.
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))

    # Kept so the order can still be traced back to a catalogue entry, for
    # "how many of these did we sell". RESTRICT, as in cart_items: a
    # product that has been sold must not be deleted out from under its
    # orders. Retiring one is what is_active is for.
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )

    # The snapshot. These are copies taken at checkout, never read back
    # from products. If the product is renamed, repriced or retired
    # tomorrow, this line still says what the customer bought and what they
    # paid - which is what an invoice has to say. Step 46 is about
    # demonstrating that this actually holds.
    sku: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    quantity: Mapped[int]

    # No created_at or updated_at on purpose. An order item never changes,
    # so updated_at could only ever repeat its creation time, and its
    # creation time is already its order's.

    order: Mapped["Order"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_is_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_not_negative"),
        # One line per product per order. The cart already guarantees it,
        # but the cart is not what this table depends on.
        Index("uq_order_items_order_id_product_id", order_id, product_id, unique=True),
    )
