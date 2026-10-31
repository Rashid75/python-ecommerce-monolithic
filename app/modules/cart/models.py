"""The carts and cart_items tables.

A cart holds what a customer intends to buy. It is working state, not a
record: it may be emptied, abandoned or replaced, and nothing depends on
being able to read it back later. Orders, in Phase 9, are the opposite, and
their rules are deliberately different.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.products.models import Product


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # One cart per customer, enforced by the unique index below rather than
    # by convention. Without it a bug that creates a second cart would show
    # a customer an empty basket while their items sit in the other one.
    #
    # ondelete="CASCADE", unlike the RESTRICT used between products and
    # categories. A cart has no meaning without its owner and no value as a
    # record, so there is nothing for anyone to decide about. An order is
    # the opposite case and must never cascade.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # cascade="all, delete-orphan" is the ORM half: removing a CartItem from
    # this list deletes its row, rather than leaving an orphan with a NULL
    # cart_id. The database half is ondelete="CASCADE" on cart_items.
    # order_by gives the lines a stable order. Without it PostgreSQL may
    # return them in any order it likes, so a cart could reshuffle itself
    # between two identical requests.
    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan", order_by="CartItem.id"
    )

    __table_args__ = (Index("uq_carts_user_id", user_id, unique=True),)


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"))

    # ondelete="RESTRICT": PostgreSQL refuses to delete a product that sits
    # in someone's cart. Retiring a product is what is_active is for;
    # deleting one that a customer is about to buy should require a
    # decision rather than silently emptying their basket.
    #
    # Deliberately no reverse relationship on Product. Category.products
    # needed passive_deletes="all" because the ORM would otherwise load the
    # children and clear their foreign key before the DELETE, bypassing
    # RESTRICT entirely. With no collection to load, there is nothing to
    # bypass.
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )

    # No price column, on purpose. A cart is not a quote. Copying the price
    # in when the item is added would show the customer a stale number for
    # as long as the cart sits there, and would create a second place where
    # prices live. The cart reads today's price from products on every
    # request. The price is frozen exactly once, when the order is created.
    quantity: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    cart: Mapped["Cart"] = relationship(back_populates="items")

    # One-directional: lets a cart line read product.name and product.price
    # without a second query, and adds no collection to Product.
    product: Mapped["Product"] = relationship()

    __table_args__ = (
        # A line holding zero of something is not a line. Removing an item
        # is a DELETE, not an update to 0.
        CheckConstraint("quantity > 0", name="quantity_is_positive"),
        # One row per product per cart. Adding the same product again
        # increases the quantity instead of creating a second line, and the
        # database is what guarantees it.
        Index("uq_cart_items_cart_id_product_id", cart_id, product_id, unique=True),
    )
