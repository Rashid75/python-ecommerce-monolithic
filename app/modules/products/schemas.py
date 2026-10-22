"""What the products API accepts and returns.

Kept separate from the SQLAlchemy model on purpose. The database row and the
API contract change for different reasons, and the model may hold columns a
client should never see.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """The body a client sends to create a product."""

    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    # ge=0 rejects a negative price with a clear 422 before it ever reaches
    # the database. The check constraint stays as the last line of defence.
    # decimal_places=2 refuses 9.999, which would otherwise be rounded
    # silently by the NUMERIC(12, 2) column.
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_active: bool = True
    # Optional: a product can exist before it is filed under a category.
    # The service checks that the category actually exists.
    category_id: int | None = None


class ProductUpdate(BaseModel):
    """A partial update. Every field is optional; only what is sent changes.

    sku is missing on purpose: it identifies the product for the business,
    so changing it would silently break invoices, reports and integrations.
    """

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    is_active: bool | None = None
    category_id: int | None = None


class ProductRead(BaseModel):
    """What the API sends back."""

    # Lets Pydantic build this straight from a SQLAlchemy object by reading
    # its attributes, instead of requiring a dictionary.
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None
    price: Decimal
    is_active: bool
    category_id: int | None
    created_at: datetime
    updated_at: datetime


# The page envelope now lives in app/common/schemas.py as Page[T], shared
# with categories. Routes return Page[ProductRead].
