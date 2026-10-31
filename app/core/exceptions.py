"""Errors the application raises, independent of HTTP.

Services raise these. The router turns them into status codes, so the
business rules never need to know what a 404 is. Step 59 adds handlers that
do that conversion in one place.
"""


class AppError(Exception):
    """Base class, so a handler can catch every application error at once."""


class NotFoundError(AppError):
    """The requested thing does not exist. The router maps this to 404."""


class AlreadyExistsError(AppError):
    """Something unique already uses that value. The router maps this to 409."""


class AuthenticationError(AppError):
    """Sign-in failed. The router maps this to 401.

    Deliberately carries one message for every cause - unknown email, wrong
    password, disabled account. Saying which one was wrong would let someone
    discover who has an account here.
    """


class InUseError(AppError):
    """Something else still refers to this, so it cannot be removed.

    The router maps this to 409 as well: the request is valid, it just
    conflicts with the current state of the data.
    """


class InsufficientStockError(AppError):
    """There is not enough stock to do what was asked.

    The router maps this to 409, like InUseError: the request is valid and
    the product exists, it just conflicts with how much is on the shelf.
    """


class ValidationError(AppError):
    """The request is well formed but breaks a business rule.

    The router maps this to 422. Distinct from Pydantic's own 422, which
    rejects a request before any rule is consulted.
    """


class UnavailableError(AppError):
    """The product cannot be bought in the quantity asked for.

    Covers both causes - the product is no longer on sale, and there is not
    enough stock - because the router maps both to 409 and the message says
    which. Distinct from InsufficientStockError, which belongs to stock
    adjustments and means an admin tried to remove more than exists.
    """


class EmptyCartError(AppError):
    """There is nothing to order. The router maps this to 409.

    Not 404: the cart exists, and not 422: the request is well formed. It
    conflicts with the state of the cart, which is what 409 is for.
    """


class PriceChangedError(AppError):
    """The total is no longer what the customer was shown. 409.

    Raised instead of charging a different amount. Carries both totals,
    because the only useful thing to tell someone is what changed.
    """
