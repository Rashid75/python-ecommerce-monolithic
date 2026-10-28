"""The products table."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.categories.models import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Stock Keeping Unit: the shop's own code for this product.
    # Uniqueness comes from the case-insensitive index in __table_args__,
    # so REL-1 and rel-1 are the same SKU.
    sku: Mapped[str] = mapped_column(String(50))

    name: Mapped[str] = mapped_column(String(200))

    # Text has no length limit. `| None` makes the column nullable.
    description: Mapped[str | None] = mapped_column(Text, default=None)

    # Numeric(12, 2) = up to 12 digits, 2 after the decimal point, stored
    # exactly. NEVER use Float for money: 0.1 + 0.2 == 0.30000000000000004
    # in floating point, and those errors add up over thousands of orders.
    # SQLAlchemy gives this back to Python as a Decimal.
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Hide a product without deleting it, so existing orders still make
    # sense. server_default must be a SQL string, not a Python bool.
    is_active: Mapped[bool] = mapped_column(server_default="true")

    # How many are on hand. A column on products rather than a separate
    # inventory table: there is one warehouse and no stock history to keep,
    # so a second table would add a join and a second row to lock for no
    # benefit. Revisit if reservations, batches or multiple locations
    # arrive - then stock genuinely becomes its own thing.
    stock_quantity: Mapped[int] = mapped_column(server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # onupdate tells SQLAlchemy to refresh this whenever the row changes.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Nullable: a product can exist before anyone decides where it belongs.
    #
    # ondelete="RESTRICT" is the important part. PostgreSQL refuses to delete
    # a category while products still point at it. The alternatives are worse:
    # CASCADE would silently delete the products along with the category, and
    # SET NULL would quietly uncategorise them. RESTRICT makes someone decide.
    #
    # index=True because every "products in this category" query filters on
    # it, and a foreign key does not get an index automatically in PostgreSQL.
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True, default=None
    )

    # Lets you write product.category in Python. Adds no column of its own.
    category: Mapped["Category | None"] = relationship(back_populates="products")

    __table_args__ = (
        # The database refuses a negative price even if application code
        # somehow allows one. A safety net under the service layer.
        CheckConstraint("price >= 0", name="price_not_negative"),
        # You cannot have minus three of something. This is the floor that
        # holds even if a concurrent checkout gets the arithmetic wrong -
        # Step 34 is about making sure it never has to.
        CheckConstraint("stock_quantity >= 0", name="stock_not_negative"),
        # Unique on lower(sku), so REL-1 and rel-1 cannot both exist.
        Index("uq_products_lower_sku", func.lower(sku), unique=True),
    )
