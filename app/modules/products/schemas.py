"""What the products API accepts and returns.

Kept separate from the SQLAlchemy model on purpose. The database row and the
API contract change for different reasons, and the model may hold columns a
client should never see.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


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
    # Opening stock. Defaults to 0, so a product that is created without
    # one simply cannot be sold until stock is added.
    stock_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    """A partial update. Every field is optional; only what is sent changes.

    sku is missing on purpose: it identifies the product for the business,
    so changing it would silently break invoices, reports and integrations.
    """

    # Pydantic drops unknown keys by default, so a client that sent
    # stock_quantity here would get 200 and believe it had worked. Rejecting
    # the request instead points them at the adjustment endpoint. Silently
    # ignoring input is worse than refusing it.
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    is_active: bool | None = None
    category_id: int | None = None
    # stock_quantity is absent on purpose. Stock moves because something
    # happened - a delivery arrived, a sale shipped, a count was corrected -
    # and those belong in explicit adjustment operations that can be made
    # atomic and recorded. A generic PATCH that sets it to a number would
    # overwrite whatever a concurrent sale just did. Step 33 adds the
    # proper endpoints.


class StockAdjustment(BaseModel):
    """A change to a product's stock, written as a difference.

    +10 means ten arrived, -2 means two left. A difference rather than a
    new total, because a total is calculated from a value read earlier and
    overwrites anything that happened since. A difference carries no such
    assumption, so two of them applied in either order give the same answer.
    """

    quantity_change: int = Field(
        description="Positive to add stock, negative to remove it. Zero is rejected."
    )

    @field_validator("quantity_change")
    @classmethod
    def reject_zero(cls, value: int) -> int:
        """A change of zero is almost always a bug in the caller.

        Allowing it would mean accepting a request that does nothing and
        reporting success, which hides the mistake.
        """
        if value == 0:
            raise ValueError("quantity_change must not be zero")
        return value


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
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

    # computed_field makes this appear in the response, which a plain
    # @property would not - a property is invisible to model_dump(). That
    # difference is deliberate elsewhere: Settings.database_url is a plain
    # property precisely so the password never lands in a dump.
    @computed_field
    @property
    def is_available(self) -> bool:
        """Whether a customer can buy this right now.

        Derived, never stored. A stored copy would be a third thing to keep
        in step with is_active and stock_quantity, and would be wrong from
        the moment either of them changed.
        """
        return self.is_active and self.stock_quantity > 0


# The page envelope now lives in app/common/schemas.py as Page[T], shared
# with categories. Routes return Page[ProductRead].
