"""What checkout accepts.

Only the request contract lives here for now. Order models arrive in Step
45 and the order read shapes with them, so that the statuses are defined
once, beside the check constraint that enforces them, rather than twice.
"""

from pydantic import BaseModel, ConfigDict, Field


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
