"""Structured logging, request correlation, and the audit trail.

Three things that are usually separate and are deliberately one file here,
because they answer the same question: when something happened, what was
it, and which request caused it.

Logs are JSON lines rather than sentences. A sentence is easy to read once
and impossible to search; `{"event": "order.created", "order_id": 14}` can
be filtered, counted and alerted on. Nothing here formats for a human,
because in production nobody reads these with their eyes.

What must NEVER be logged: passwords, tokens, card data, webhook secrets,
and the personal fields of an address - recipient name, phone, street,
postal code. The audit events below carry ids, statuses and amounts, which
are what an auditor needs, and never the personal data those ids point at.
"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# The id of the request being handled, readable from anywhere without
# passing it through every function signature. A ContextVar is per-task,
# so two requests handled at once never see each other's value.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# Keys a LogRecord always has. Anything else an event carries is extra, and
# gets copied into the JSON line.
_STANDARD = frozenset(
    set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__)
    | {"asctime", "message", "taskName"}
)


class JsonFormatter(logging.Formatter):
    """One JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD:
                payload[key] = value
        if record.exc_info:
            # The traceback goes in the log and never in a response.
            payload["traceback"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Send every log through the JSON formatter. Called once, from main."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # uvicorn installs its own handlers and would otherwise print its own
    # format alongside ours, giving two shapes of line in one stream.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Give every request an id, and log one line when it finishes.

    An incoming X-Request-ID is honoured so that a trace started by a load
    balancer or another service continues here rather than restarting. It
    is length-limited and stripped of anything unusual, because it is
    attacker-controlled text that ends up in log files that something else
    will parse.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        incoming = request.headers.get("X-Request-ID", "")
        request_id = _clean_request_id(incoming) or uuid.uuid4().hex
        token = request_id_var.set(request_id)

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # The exception handler will turn this into a 500 and log the
            # traceback; this line records that the request ended badly,
            # with its timing, so the two can be matched by request_id.
            logging.getLogger("app.access").exception(
                "request failed",
                extra={
                    "event": "http.request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": 500,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                },
            )
            request_id_var.reset(token)
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        logging.getLogger("app.access").info(
            "request",
            extra={
                "event": "http.request",
                "method": request.method,
                # The path template, not the path: /orders/{order_id}
                # rather than /orders/14. Grouping by template is what
                # makes latency per endpoint meaningful, and it keeps ids
                # out of the message field.
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Echoed back so a client, or whoever is reading a support ticket,
        # can quote the id that finds this request in the logs.
        response.headers["X-Request-ID"] = request_id
        request_id_var.reset(token)
        return response


def _clean_request_id(value: str) -> str:
    """Keep only a short, boring id. Reject anything else."""
    cleaned = "".join(c for c in value if c.isalnum() or c in "-_")
    return cleaned[:64]


audit_logger = logging.getLogger("app.audit")


def audit(event: str, **fields: Any) -> None:
    """Record something that must still be explainable months later.

    Separate from ordinary logging by name, so these lines can be shipped
    to different storage with a different retention period and - the part
    that matters for an audit trail - storage that the application cannot
    edit or delete.

    Pass ids, statuses and amounts. Never personal data: an order id leads
    an authorised person to the address, while an address in a log file
    leads anyone with log access to the customer.
    """
    audit_logger.info(event, extra={"event": event, **fields})
