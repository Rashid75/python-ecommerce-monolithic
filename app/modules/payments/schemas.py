"""What the payment endpoints accept and return."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.modules.payments.models import PaymentStatus


class PaymentRead(BaseModel):
    """A payment as the customer sees it.

    No provider reference: it is the provider's identifier, useful for
    support and reconciliation, and nothing a customer's browser needs. The
    less of the provider's vocabulary that leaks into this API, the less
    that breaks when the provider changes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    created_at: datetime


class PaymentStarted(PaymentRead):
    """What starting a payment returns: the record, plus what to do next."""

    instructions: str
