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
