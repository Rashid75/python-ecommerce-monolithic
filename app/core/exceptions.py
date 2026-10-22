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
