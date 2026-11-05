"""One place that turns an application error into an HTTP response.

Before this, every router caught every exception it could raise and chose a
status code. The same mapping was written out eleven times, which is eleven
chances for one endpoint to answer 403 where the others answer 404 - and
that difference is exactly what an attacker reads.

Now a service raises and says nothing about HTTP, a router calls it and
catches nothing, and the mapping below is the only place a status code is
decided.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AlreadyExistsError,
    AppError,
    AuthenticationError,
    BusyError,
    EmptyCartError,
    InsufficientStockError,
    InUseError,
    InvalidTransitionError,
    NotFoundError,
    PriceChangedError,
    SignatureError,
    UnavailableError,
    ValidationError,
)

logger = logging.getLogger("app.errors")

# Every application error, and the one status code it means. A new error
# class that is not listed here falls through to 500, which is loud enough
# to notice in testing and safe enough not to leak anything in production.
STATUS_FOR: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    SignatureError: status.HTTP_400_BAD_REQUEST,
    ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    # Everything below is 409: the request was well formed and the thing it
    # names exists; it conflicts with the current state of the data.
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    InUseError: status.HTTP_409_CONFLICT,
    InsufficientStockError: status.HTTP_409_CONFLICT,
    UnavailableError: status.HTTP_409_CONFLICT,
    EmptyCartError: status.HTTP_409_CONFLICT,
    PriceChangedError: status.HTTP_409_CONFLICT,
    InvalidTransitionError: status.HTTP_409_CONFLICT,
    BusyError: status.HTTP_503_SERVICE_UNAVAILABLE,
}

# A stable, machine-readable name for each error, so a client can branch on
# something that will not change when the wording of a message does.
CODE_FOR: dict[type[AppError], str] = {
    NotFoundError: "not_found",
    AuthenticationError: "authentication_failed",
    SignatureError: "bad_signature",
    ValidationError: "validation_failed",
    AlreadyExistsError: "already_exists",
    InUseError: "in_use",
    InsufficientStockError: "insufficient_stock",
    UnavailableError: "unavailable",
    EmptyCartError: "empty_cart",
    PriceChangedError: "price_changed",
    InvalidTransitionError: "invalid_transition",
    BusyError: "busy",
}


def _body(detail: str, code: str) -> dict[str, Any]:
    """The one error shape this API returns.

    `detail` stays the key FastAPI already uses, so nothing that reads it
    has to change. `code` is the part worth branching on.
    """
    return {"detail": detail, "code": code}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the handlers. Called once, from main."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        # type(exc) rather than isinstance checks, so a subclass added later
        # does not silently inherit a parent's status code.
        code = STATUS_FOR.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        if code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(
                "unmapped application error",
                extra={"event": "error.unmapped", "error_type": type(exc).__name__},
            )
            return JSONResponse(
                status_code=code,
                content=_body("Something went wrong. Please try again.", "internal_error"),
            )
        # WWW-Authenticate tells a client which scheme to use. It used to
        # be set by hand on the login endpoint; here it covers every 401
        # the application can produce, which is what centralising is for.
        headers = {"WWW-Authenticate": "Bearer"} if code == status.HTTP_401_UNAUTHORIZED else None
        return JSONResponse(
            status_code=code,
            content=_body(str(exc), CODE_FOR.get(type(exc), "error")),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # FastAPI's own 422, reshaped to carry a code like everything else.
        # The per-field errors are kept: they describe the request the
        # client sent, not anything internal.
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors(), "code": "request_invalid"},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # The whole point of this handler. Anything unforeseen - a bug, a
        # dropped connection, a library raising something new - is logged
        # with its traceback and answered with a sentence that says
        # nothing. Exception text routinely contains table names, SQL,
        # file paths and occasionally values from the row that failed.
        logger.exception(
            "unhandled exception",
            extra={"event": "error.unhandled", "error_type": type(exc).__name__},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_body("Something went wrong. Please try again.", "internal_error"),
        )
