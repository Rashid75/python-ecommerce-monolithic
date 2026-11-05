"""The boundary between this shop and whoever moves the money.

Everything above this file talks about payments in general terms. Only the
provider implementations below know what any particular company's API looks
like, so swapping one for another touches this file and nothing else.
"""

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.core.config import get_settings
from app.core.exceptions import SignatureError, ValidationError


@dataclass(frozen=True)
class PaymentIntent:
    """What a provider gives back when a payment is started.

    Deliberately not a confirmation. Creating an intent means the provider
    is ready to be paid, not that anyone has paid - that only ever arrives
    as a webhook.
    """

    reference: str
    instructions: str


@dataclass(frozen=True)
class WebhookEventData:
    """One event, after its signature has been checked."""

    event_id: str
    event_type: str
    reference: str


class PaymentProvider(Protocol):
    """What the rest of the application may assume about a provider."""

    name: str

    def create_payment(self, order_id: int, amount: Decimal, currency: str) -> PaymentIntent:
        """Start a payment and return the provider's reference for it."""
        ...

    def start_refund(self, reference: str, amount: Decimal) -> str:
        """Ask for a refund and return the provider's reference for it.

        Asking is not the same as being refunded. The money is only back
        when the provider says so in a webhook.
        """
        ...

    def read_webhook(self, raw_body: bytes, signature: str) -> WebhookEventData:
        """Check the signature and parse the event, or raise."""
        ...


class SandboxProvider:
    """A stand-in for a real provider, for local development only.

    This moves no money and talks to nobody. It exists so the rest of the
    system - intents, webhooks, signatures, duplicate events, refunds - can
    be built and tested before a contract with a real provider exists.

    It does NOT ever mark a payment as succeeded by itself. A payment here
    becomes succeeded exactly as it would in production: when a signed
    webhook says so. During development that webhook is sent by hand or by
    a test holding the same secret, which is why the secret is a real
    secret and not a constant in this file.

    Refusing to run in production is enforced in Settings, not here, so
    that the application fails at startup rather than at the first payment.
    """

    name = "sandbox"

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    def create_payment(self, order_id: int, amount: Decimal, currency: str) -> PaymentIntent:
        reference = f"sandbox_{uuid.uuid4().hex}"
        return PaymentIntent(
            reference=reference,
            instructions=(
                f"Sandbox provider: no money will move. Order {order_id} is awaiting "
                f"{amount} {currency}. This payment becomes succeeded only when a signed "
                f"webhook for {reference} is received."
            ),
        )

    def start_refund(self, reference: str, amount: Decimal) -> str:
        return f"sandbox_refund_{uuid.uuid4().hex}"

    def sign(self, raw_body: bytes) -> str:
        """Produce the signature this provider would send.

        Public because the webhook sender needs it. In production that
        sender is the provider; here it is a test or a developer, and
        either way they must hold the shared secret.
        """
        return hmac.new(self._secret, raw_body, hashlib.sha256).hexdigest()

    def read_webhook(self, raw_body: bytes, signature: str) -> WebhookEventData:
        expected = self.sign(raw_body)

        # compare_digest, not ==. A normal comparison returns as soon as
        # two bytes differ, so how long it takes leaks how much of the
        # signature was right, and a patient attacker can guess one byte at
        # a time. This takes the same time whatever the input.
        if not hmac.compare_digest(expected, signature or ""):
            raise SignatureError("The signature does not match the body")

        # Parsed only after the signature passes. Handing unverified bytes
        # to a parser is work done on behalf of whoever sent them.
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise SignatureError("The body is not valid JSON") from exc

        try:
            return WebhookEventData(
                event_id=str(body["id"]),
                event_type=str(body["type"]),
                reference=str(body["reference"]),
            )
        except (KeyError, TypeError) as exc:
            raise SignatureError("The event is missing id, type or reference") from exc


def get_provider() -> PaymentProvider:
    """The provider this environment is configured to use."""
    settings = get_settings()
    if settings.payment_provider == "sandbox":
        return SandboxProvider(settings.payment_webhook_secret.get_secret_value())
    # Unreachable while Literal["sandbox"] is the only option, and kept so
    # that adding a provider fails loudly here rather than silently
    # returning the sandbox one.
    raise ValidationError(f"Unknown payment provider: {settings.payment_provider}")
