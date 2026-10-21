"""The products table."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Stock Keeping Unit: the shop's own code for this product.
    # unique=True also creates an index, which makes lookups by sku fast.
    sku: Mapped[str] = mapped_column(String(50), unique=True)

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

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # onupdate tells SQLAlchemy to refresh this whenever the row changes.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # The database refuses a negative price even if application code
        # somehow allows one. A safety net under the service layer.
        CheckConstraint("price >= 0", name="price_not_negative"),
    )
